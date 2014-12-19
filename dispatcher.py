import asyncio
import json
import logging
logger = logging.getLogger('websockets.dispatcher')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

dispatcher_map = dict()


class Message(object):
    def __init__(self, msg_uri, data=None):
        super(Message, self).__init__()
        self.msg_uri = msg_uri
        self.data = data

    @asyncio.coroutine
    def dispatch(self, websocket):
        logger.debug("TX: {} - {}".format(self.msg_uri, repr(self.data)))
        info = {
            'cmd': self.msg_uri,
        }
        if self.data is not None:
            info["data"] = self.data
        json_info = json.dumps(info)
        asyncio.async(websocket.send(json_info))


def response(msg_uri, data=None):
    return Message(msg_uri, data)


def ws_message(msg_uri):
    """
    Decorator for message dispatching
    :param msg_uri:
    :return:
    """
    msg_uri = msg_uri.lower()

    def wrap(f):
        if msg_uri in dispatcher_map:
            logger.warning("URI already defined: {}".format(msg_uri))

        def wrapped_f(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, Message):
                # args[0] MUST be the websocket in the message
                asyncio.async(result.dispatch(args[0]))
            elif result is not None:
                logger.warning("Function decorated with 'ws_message' "
                               "should return a Message or None")
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


def send_message(websocket, msg_uri, data=None):
    call = Message(msg_uri, data)
    asyncio.async(call.dispatch(websocket))


# Pre-defined handlers
@ws_message("_pong")
def _pong(websocket, msg):
    pass
