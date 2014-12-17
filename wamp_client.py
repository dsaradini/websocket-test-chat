try:
    import asyncio
except ImportError:
    ## Trollius >= 0.3 was renamed
    import trollius as asyncio

from autobahn.asyncio import wamp, websocket
import ws_const
import sys


class MyFrontendComponent(wamp.ApplicationSession):
    CHANNEL = ws_const.CHANNEL

    def onConnect(self):
        self.join(ws_const.REALM,
                  authmethods=["exodoc-ticket"],
                  authid="good-ticket-Client one")

    def input_handle(self, line):
        try:
            # self.publish(ws_const.CHANNEL, line)
            self.call(ws_const.MSG_SEND_MESSAGE, line)
        except Exception as e:
            print("Error: {}".format(e))

    @asyncio.coroutine
    def onJoin(self, details):
        print("On join: {}".format(details))
        self.in_task = asyncio.get_event_loop().add_reader(
            sys.stdin.fileno(),
            lambda *args: self.input_handle(sys.stdin.readline()))

        def on_message(message):
            print("Message: {}".format(message))

        sub = yield from self.subscribe(on_message, self.CHANNEL)
        print("Subscribed with subscription ID {}".format(sub.id))

    def onLeave(self, details):
        print("Leave: {}".format(details))
        self.in_task.close()
        self.disconnect()

    def onDisconnect(self):
        print("on-disconnect")
        asyncio.get_event_loop().stop()


if __name__ == '__main__':

    ## 1) create a WAMP application session factory
    session_factory = wamp.ApplicationSessionFactory()
    session_factory.session = MyFrontendComponent

    ## 2) create a WAMP-over-WebSocket transport client factory
    transport_factory = websocket.WampWebSocketClientFactory(
        session_factory, debug=False, debug_wamp=False)

    ## 3) start the client
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(
        transport_factory, ws_const.CONNECT_ADDRESS, ws_const.PORT)
    loop.run_until_complete(coro)
    ## 4) now enter the asyncio event loop
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
