import asyncio
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

@ws_message("ch.exodoc.new_message")
def receive_chat(websocket, msg):
    print("\r[{}] {}".format(msg['user'], msg['text']))


@asyncio.coroutine
def _connect(name):
    while not hasattr(websocket, "value"):
        try:
            websocket.value = yield from websockets.connect(
                'ws://{}:{}/?name={}'.format(
                    ws_const.CONNECT_ADDRESS,
                    ws_const.PORT,
                    name
                ))
        except ConnectionRefusedError:
            print("Retry connection")
            yield from asyncio.sleep(2)


@asyncio.coroutine
def message_handler(name='anonymous'):
    while asyncio.get_event_loop().is_running():
        yield from _connect(name)
        print("Connected to server as {}".format(name))
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

if __name__ == "__main__":
    name = "python_client"
    loop = asyncio.get_event_loop()
    try:
        loop.add_reader(
            sys.stdin.fileno(),
            lambda *args: asyncio.async(input_handle(sys.stdin.readline()))
        )
        loop.run_until_complete(message_handler(name))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Client stopped")