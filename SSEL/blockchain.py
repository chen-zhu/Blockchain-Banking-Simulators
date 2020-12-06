import sys
import json
import copy
import random
import string
import time
import copy
import threading
import zerorpc
from pprint import pprint
from Lib.helper import *
import numpy as np

port_lowerRange = int(sys.argv[1])
port_upperRange = int(sys.argv[2])
blockChainAddress = "tcp://0.0.0.0:5000"
genesis = []
registration = {}
clientSecrets = []
lock = threading.Lock()

elected_flag = 0
selected_client_id = 0

#Handle Leader Election
class blockChain(object):
    def Register(self, client_id, client_name, round_num):
    	global registration, lock
    	client_id = int(client_id)
    	#if round_num != len(genesis) + 1:
    	#	return 0 
    	#lock.acquire()
    	registration[client_id] = client_name
    	clientSecrets.append(client_id)
    	#lock.release()
    	print(">> Register from client [" + str(client_id) + "] received!" )
    	#pprint(registration)
    	#pprint(clientSecrets)
    	return 1

    def Revoke(self, client_id):
    	global elected_flag
    	clientSecrets.remove(selected_client_id)
    	tmp = registration.pop(selected_client_id, None)
    	elected_flag = 0
    	print(">> Revoke from client [" + client_id + "] received.")
    	#pprint(registration)
    	#pprint(clientSecrets)

#let other participants to verify
#def RegisterVerify(): 

def Elect():
	global clientSecrets, selected_client_id, port_lowerRange, port_upperRange, lock
	lock.acquire()
	rand_val = np.random.randint(low=port_lowerRange, high=port_upperRange+1)
	array = np.asarray(clientSecrets)
	idx = (np.abs(array - rand_val)).argmin()
	selected_client_id = array[idx]
	print("<< Leader Elected: client [" + str(selected_client_id) + "]. Random Val Chosen: " + str(rand_val))
	#print("[DEBUG]: Change elected_flag to 1")
	elected_flag = 1
	#Let the leader know~
	c = zerorpc.Client()
	c.connect("tcp://0.0.0.0:" + str(selected_client_id))
	c.Distributor('Elect', str(selected_client_id)) #send selected_cleint_id as proof here~
	c.close()
	lock.release()


def ear(): 
	s = zerorpc.Server(blockChain(), pool_size=1000, heartbeat=None)
	s.bind(blockChainAddress)
	s.run()

#create a thread to handle 'listening'
listen_thread = threading.Thread(target=ear, args=())
listen_thread.start()

#Add trx
while True:
	#time.sleep(0.1)
	#print("[DEBUG]: While True" + str(len(clientSecrets)) + " -- " + str(elected_flag))
	if len(clientSecrets) > 0 and elected_flag == 0: 
		print("\n__________________New Leader Election_______________________")
		Elect()
		
		
		




