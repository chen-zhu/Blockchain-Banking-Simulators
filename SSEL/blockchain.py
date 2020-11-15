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
    	global registration
    	client_id = int(client_id)
    	#if round_num != len(genesis) + 1:
    	#	return 0 
    	registration[client_id] = client_name
    	clientSecrets.append(client_id)
    	print("Register received.")
    	pprint(registration)
    	pprint(clientSecrets)
    	return 1

    def Revoke(self, client_id):
    	global elected_flag
    	clientSecrets.remove(selected_client_id)
    	tmp = registration.pop(selected_client_id, None)
    	elected_flag = 0
    	print("Revoke received.")
    	pprint(registration)
    	pprint(clientSecrets)

#let other participants to verify
#def RegisterVerify(): 

def Elect():
	global clientSecrets, selected_client_id
	print(clientSecrets)
	rand_val = np.random.randint(low=49999, high=60000)
	array = np.asarray(clientSecrets)
	idx = (np.abs(array - rand_val)).argmin()
	selected_client_id = array[idx]
	print("[DEBUG]: Change elected_flag to 1")
	elected_flag = 1
	#Let the leader know~
	c = zerorpc.Client()
	c.connect("tcp://0.0.0.0:" + str(selected_client_id))
	c.Distributor('Elect', str(selected_client_id)) #send selected_cleint_id as proof here~


def ear(): 
	s = zerorpc.Server(blockChain())
	s.bind(blockChainAddress)
	s.run()

#create a thread to handle 'listening'
listen_thread = threading.Thread(target=ear, args=())
listen_thread.start()

#Add trx
while True:
	time.sleep(5)
	print("[DEBUG]: While True" + str(len(clientSecrets)) + " -- " + str(elected_flag))
	if len(clientSecrets) > 0 and elected_flag == 0: 
		Elect()
		
		
		




