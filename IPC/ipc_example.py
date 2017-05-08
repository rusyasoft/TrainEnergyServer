""" ipc_example.py
Usage:
    ipc_example.py server [options]
    ipc_example.py client [options] <class> [--arg=<arg>...] [--kwarg=<kwarg>...]
Options:
    -p --port=<port>      The port number to communicate over [default: 5795]
    -h --host=<host>      The host name to communicate over [default: localhost]
    -s --socket=<socket>  A socket file to use, instead of a host:port
    -a --arg=<arg>        A positional arg to supply the class constructor
    -k --kwarg=<kwarg>    A keyword arg to supply the class constructor
"""

import docopt
import ipc


class Event(ipc.Message):
    def __init__(self, event_type, **properties):
        self.type = event_type
        self.properties = properties

    def _get_args(self):
        return [self.type], self.properties


class Response(ipc.Message):
    def __init__(self, text):
        self.text = text

    def _get_args(self):
        return [self.text], {}


def server_process_request(objects):
    response = [Response('Recieved {} objects'.format(len(objects)))]
    print 'Recieved objects: {}'.format(objects)
    print 'Sent objects: {}'.format(response)
    return response


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    server_address = args['--socket'] or (args['--host'], int(args['--port']))

    if args['server']:
        ipc.Server(server_address, server_process_request).serve_forever()

    if args['client']:
        kwargs = {k: v for k, v in [i.split('=', 1) for i in args['--kwarg']]}
        user_input = [{'class': args['<class>'], 'args': args['--arg'], 'kwargs': kwargs}]
        objects = ipc.Message.deserialize(user_input)
        print 'Sending objects: {}'.format(objects)
        with ipc.Client(server_address) as client:
            response = client.send(objects)
        print 'Recieved objects: {}'.format(response)


# Example usage:
#     $ ./ipc_example.py server
#     then in another terminal:
#     $ ./ipc_example.py client Event --arg=testevent --kwarg=exampleproperty=examplevalue


