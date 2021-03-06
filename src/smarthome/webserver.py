
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen

from queue import Queue, Empty

from .IoticRecv import IoticRecv


WEB_SERVER_ADDRESS = ('0.0.0.0', 8888)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('../static/index.html')


clients = []
queue = Queue()
runner = None

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WS/ New connection")
        clients.append(self)

    def on_close(self):
        print("WS/ Connection closed")
        clients.remove(self)

    def on_message(self, msg):
        global runner
        print("WS/ Got message", msg)
        if msg == 'vol_up':
            runner.snd_ctrl_vol_up()
        elif msg == 'vol_down':
            runner.snd_ctrl_vol_down()
        #
        if msg == 'lamp_on':
            runner.lamp_ctrl_on()
        elif msg == 'lamp_off':
            runner.lamp_ctrl_off()
        #
        if msg in ['upstairs_lamp_off', 'upstairs_lamp_on', 'bedroom_lamp_off', 'bedroom_lamp_on', 'liv_main_off', 'liv_main_on', 'kitchen_lamp_on', 'kitchen_lamp_off', 'front_lamp_on', 'front_lamp_off']:
            if msg.endswith('_off'):
                cmd = 'off'
                msg = msg.replace('_off', '')
            else:
                cmd = 'on'
                msg = msg.replace('_on', '')
            runner.lights_ctrl(msg, cmd)


def broadcast_update():
    global queue
    try:
        while True:
            results = queue.get(False)
            for c in clients:
                c.write_message(results)
    except Empty:
        pass


def main():
    global runner, queue
    runner = IoticRecv('../cfg/smarthome.ini', queue)
    runner.run(background=True)

    settings = {
        'debug': True
    }
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': '/home/pi/smarthome.git/src/static/'}),
        ], **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(WEB_SERVER_ADDRESS[1], WEB_SERVER_ADDRESS[0])
    print("Listening on port:", WEB_SERVER_ADDRESS[1])

    try:
        main_loop = tornado.ioloop.IOLoop.instance()
        scheduler = tornado.ioloop.PeriodicCallback(broadcast_update, 1000, io_loop=main_loop)
        scheduler.start()
        main_loop.start()
    except:
        pass
    finally:
        runner.stop()
