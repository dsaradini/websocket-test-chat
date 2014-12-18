import asyncio
import json
import logging
logger = logging.getLogger('websockets.dispatcher')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

dispatcher_map = dict()


def ws_message(msg_uri):
    msg_uri = msg_uri.lower()

    def wrap(f):
        if msg_uri in dispatcher_map:
            logger.warning("URI already defined: {}".format(msg_uri))

        def wrapped_f(*args, **kwargs):
            return f(*args, **kwargs)
        dispatcher_map[msg_uri] = wrapped_f
        logger.debug("Register message dispatcher: {}".format(msg_uri))
        return wrapped_f
    return wrap


def handle_message(websocket, raw_msg):
    msg = json.loads(raw_msg)
    if 'cmd' in msg:
        cmd = msg['cmd']
        data = msg.get('data', None)
        fun = dispatcher_map.get(cmd.lower(), None)
        logger.debug("RX: {} - {}".format(cmd, repr(data)))
        if fun:
            asyncio.get_event_loop().call_soon(
                fun, websocket, data)
        else:
            logger.warning("Unknown message: {}".format(cmd))
    else:
        logger.warning("Not a valid message: {}".format(raw_msg))


def send_message(websocket, msg_uri, data):
    logger.debug("TX: {} - {}".format(msg_uri, repr(data)))
    info = json.dumps({
        'cmd': msg_uri,
        'data': data
    })
    asyncio.async(websocket.send(info))
