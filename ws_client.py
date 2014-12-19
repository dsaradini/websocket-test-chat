import asyncio
import getpass
import requests
import websockets
import sys
from threading import local

from dispatcher import ws_message, handle_message, send_message
import settings as ws_const

import logging
logger = logging.getLogger('websockets.client')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

websocket = local()

# Registered action in realm
@ws_message("ch.exodoc.new_message")
def receive_chat(websocket, msg):
    print("\r[{}] {}".format(msg['user'], msg['text']))


@ws_message("ch.exodoc.join")
def join_chat(websocket, msg):
    print("\r* User '{}' joined the chat".format(msg['user']))


@ws_message("ch.exodoc.leave")
def leave_chat(websocket, msg):
    print("\r* User '{}' leave the chat".format(msg['user']))


@asyncio.coroutine
def _connect(ticket):
    while not hasattr(websocket, "value"):
        try:
            websocket.value = yield from websockets.connect(
                'ws://{}:{}/?ticket={}'.format(
                    ws_const.CONNECT_ADDRESS,
                    ws_const.PORT,
                    ticket
                ))
        except ConnectionRefusedError:
            print("Retry connection")
            yield from asyncio.sleep(2)


@asyncio.coroutine
def message_handler(username, password):
    while asyncio.get_event_loop().is_running():
        ticket = yield from login(username, password)
        yield from _connect(ticket)
        print("Connected to server with ticket {}".format(ticket))
        while True:
            msg = yield from websocket.value.recv()
            if msg:
                try:
                    handle_message(websocket.value, msg)
                except Exception as ex:
                    logger.error("Receive error: {}".format(ex))
            else:
                break
        del websocket.value
        print("Client disconnected")


@asyncio.coroutine
def input_handle(line):
    # print("Send message: {}".format(line))
    if hasattr(websocket, "value"):
        send_message(websocket.value, 'ch.exodoc.send_message', line)
    else:
        logger.info("Not connected yet")


@asyncio.coroutine
def login(username, password):
    response = yield from asyncio.get_event_loop().run_in_executor(
        None, requests.post, 'http://localhost:5000/token', None, {
            'username': username,
            'password': password
        })
    if response.status_code not in [200, 201]:
        raise Exception("Unable to login, bad username or password")
    return response.json()['ticket']


@asyncio.coroutine
def pinger():
    while True:
        if hasattr(websocket, "value"):
            send_message(websocket.value, '_ping')
        yield from asyncio.sleep(2)


if __name__ == "__main__":
    username = input("Username:").strip()
    password = getpass.getpass("Password:")
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    try:
        loop.add_reader(
            sys.stdin.fileno(),
            lambda *args: asyncio.async(input_handle(sys.stdin.readline()))
        )
        asyncio.async(message_handler(username, password), loop=loop)
        asyncio.async(pinger(), loop=loop)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Client stopped")
