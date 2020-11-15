import zerorpc

c = zerorpc.Client()
c.connect("tcp://0.0.0.0:50000")
print(c.hello("RPC"))