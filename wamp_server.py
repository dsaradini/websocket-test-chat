import random
import string

from autobahn.asyncio import wamp, websocket
from autobahn.wamp.types import ComponentConfig
from autobahn.wamp import types, register

try:
    import asyncio
except ImportError:
    ## Trollius >= 0.3 was renamed
    import trollius as asyncio

import ws_const


def generate_random_string(l=15):
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits + "-._+"
    ) for _ in range(l))


class ServerComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super(ServerComponent, self).__init__(config)

    @register(ws_const.MSG_SEND_MESSAGE)
    def send_message(self, message, details=None):
        print("details={}".format(details))
        full_message = "[{0}] {1}".format(
            details.authid,
            message
        )
        self.publish(ws_const.CHANNEL, full_message)
        return True

    @asyncio.coroutine
    def onJoin(self, details):
        print("Server ready {}".format(details))
        try:
            yield from self.register(
                self, options=types.RegisterOptions(
                    details_arg='details',
                    discloseCaller=True
                ))
            print("procedure registered")
        except Exception as e:
            print("could not register procedure: {0}".format(e))


class ClientSession(wamp.RouterSession):

    def onHello(self, realm, details):
        print("On hello: {}".format(details))
        if u"exodoc-ticket" not in details.authmethods:
            return types.Deny(
                u"wamp.error.not_authorized",
                message=u"Only 'exodoc-ticket' supported as authmethods")
        if not details.authid.startswith("good-ticket-"):
            return types.Deny(
                u"wamp.error.not_authorized",
                message=u"Bad credential")

        self._authid = details.authid[len("good-ticket-"):]
        self._authmethod = u"exodoc-ticket"
        self._authrole = u"chatter"
        self._authprovider = u"redis-token"
        return types.Accept(
            authid=self._authid,
            authrole=self._authrole,
            authmethod=self._authmethod,
            authprovider=self._authprovider,
        )


class ServerRouter(wamp.Router):

    def authorize(self, session, uri, action):
        print("MyRouter.authorize: {} {} {}".format(session, uri, action))
        return True


if __name__ == '__main__':

    ## 1) create a WAMP router factory
    router_factory = wamp.RouterFactory()
    router_factory.router = ServerRouter

    ## 2) create a WAMP router session factory
    session_factory = wamp.RouterSessionFactory(router_factory)
    session_factory.session = ClientSession

    ## 3) Optionally, add embedded WAMP application sessions to the router
    session_factory.add(ServerComponent(ComponentConfig(
        realm=ws_const.REALM,
    )))

    ## 4) create a WAMP-over-WebSocket transport server factory
    transport_factory = websocket.WampWebSocketServerFactory(
        session_factory, debug=False, debug_wamp=False)

    ## 5) start the server
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        transport_factory, ws_const.BIND_ADDRESS, ws_const.PORT)
    server = loop.run_until_complete(coro)

    try:
        ## 6) now enter the asyncio event loop
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
