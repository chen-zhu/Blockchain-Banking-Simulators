import zerorpc

class HelloRPC(object):
    def hello(self, name):
    	print("Hello")
    	return "Hello, %s" % name

s = zerorpc.Server(HelloRPC())
s.bind("tcp://0.0.0.0:50000")
s.run()