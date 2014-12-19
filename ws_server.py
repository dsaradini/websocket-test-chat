import asyncio
from collections import defaultdict
import json
import websockets
import asyncio_redis
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from dispatcher import ws_message, handle_message, send_message, response
import settings as ws_const

import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


CLIENTS = []
BY_USER_CLIENTS = defaultdict(list)


def add_client(client):
    CLIENTS.append(client)
    BY_USER_CLIENTS[client._user_name].append(client)
    logger.info("New client: {}".format(client._user_name))


def remove_client(client):
    CLIENTS.remove(client)
    BY_USER_CLIENTS[client._user_name].remove(client)
    logger.info("Client disconnected: {}".format(client._user_name))


@ws_message("_ping")
def _ping(websocket, msg):
    return response("_pong")


@ws_message("ch.exodoc.send_message")
def broadcast_chat(websocket, msg):
    for c in CLIENTS:
        send_message(c, "ch.exodoc.new_message", {
            'text': msg.strip(),
            'user': websocket._user_name,
            'date': datetime.now().isoformat(),
            'self': (websocket == c)
        })


@asyncio.coroutine
def broadcast_join(websocket):
    for c in CLIENTS:
        send_message(c, "ch.exodoc.join", {
            'user': websocket._user_name
        })


@asyncio.coroutine
def broadcast_leave(websocket):
    for c in CLIENTS:
        if websocket != c:
            send_message(c, "ch.exodoc.leave", {
                'user': websocket._user_name
            })


@asyncio.coroutine
def get_ticket_info(ticket):
    if ticket == "_test":
        return {
            'username': "TEST"
        }
    # Create Redis connection
    connection = yield from asyncio_redis.Connection.create(
        host='localhost', port=6379)

    # Set a key
    key = 'ch.exodoc:{}'.format(ticket)
    data = yield from connection.get(key)
    logger.debug("DATA : {} = {}".format(key, data))
    # When finished, close the connection.
    connection.close()
    return json.loads(data) if data else None


@asyncio.coroutine
def ws_handler(websocket, path):
    url_info = urlparse(path)
    query = parse_qs(url_info.query)
    ticket = query.get("ticket", None)
    if not ticket:
        raise Exception("Missing ticket")
    else:
        ticket_info = yield from get_ticket_info(ticket[0])
        if not ticket_info:
            raise Exception("Bad ticket")
    websocket._user_name = ticket_info['username']
    add_client(websocket)
    yield from broadcast_join(websocket)
    while True:
        message = yield from websocket.recv()
        if message is None:
            break
        else:
            try:
                handle_message(websocket, message)
            except Exception as ex:
                logger.error("Receive error: {}".format(ex))
    remove_client(websocket)
    yield from broadcast_leave(websocket)


def do_start():
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(
        ws_handler, ws_const.BIND_ADDRESS, ws_const.PORT)
    try:
        loop.run_until_complete(start_server)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Server stopped")


if __name__ == "__main__":
    do_start()