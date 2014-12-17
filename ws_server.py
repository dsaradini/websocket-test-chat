import asyncio
import websockets
from urllib.parse import urlparse, parse_qs

from dispatcher import ws_message, handle_message, send_message
import settings as ws_const

import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


CLIENTS = []

@ws_message("ch.exodoc.send_message")
def send_chat(websocker, msg):
    for c in CLIENTS:
        send_message(c, "ch.exodoc.new_message", {
            'text': msg.strip(),
            'user': websocker._user_name
        })


@asyncio.coroutine
def ws_handler(websocket, path):
    url_info = urlparse(path)
    query = parse_qs(url_info.query)
    name = query.get("name", ["anonymous"])
    websocket._user_name = name[0]
    CLIENTS.append(websocket)
    logger.info("New client: {} - {}".format(repr(websocket), path))
    while True:
        message = yield from websocket.recv()
        if message is None:
            break
        else:
            try:
                handle_message(websocket, message)
            except Exception as ex:
                logger.error("Receive error: {}".format(ex))
    logger.info("Client disconnected: {}".format(websocket))
    CLIENTS.remove(websocket)


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