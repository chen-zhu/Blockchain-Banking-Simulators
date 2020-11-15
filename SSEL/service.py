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

lock = threading.Lock()

client_id = sys.argv[1]
client_name = sys.argv[2]
client_port = client_id
client_ip = "tcp://127.0.0.1"

port_lowerRange = int(sys.argv[3])
port_upperRange = int(sys.argv[4])

registered = 0
current_trx = {}

#*********************BlockcChain Main Body Function************************
genesis = []
commits = []
blockChainAddress = "tcp://127.0.0.1:5000"

def check_balance():
	initial_balance = 100
	global genesis, commits, client_name
	#calculate aggregated list
	for commits_block in genesis:
		for trx in commits_block: 
			if trx['from'] == client_name:
				initial_balance -= int(trx['amt'])
			elif trx['to'] == client_name: 
				initial_balance += int(trx['amt'])
	#calculate commits list
	for trx in commits: 
		if trx['from'] == client_name:
			initial_balance -= int(trx['amt'])
		elif trx['to'] == client_name: 
			initial_balance += int(trx['amt'])
	return initial_balance

def broadcast(trx, leader_secret, proof): 
	global port_lowerRange, port_upperRange, client_port
	for i in range(port_lowerRange, port_upperRange + 1): 
		#do not broadcast to self!
		if str(i) == str(client_port):
			continue;
		c = zerorpc.Client()
		c.connect("tcp://0.0.0.0:" + str(i))
		data = json.dumps([trx, leader_secret, proof])
		c.Distributor('Verify', data)


#********************* Single Secret Leader Election ************************
def Register(): 
	global registered, blockChainAddress, client_id, client_name, genesis
	print("Register User On Blockchain Network...")
	registered = 1
	c = zerorpc.Client()
	c.connect(blockChainAddress)
	ret = c.Register(client_id, client_name, len(genesis) + 1)
	return True if (ret == 1) else False

def Revoke():
	global registered, blockChainAddress, client_id, client_name, genesis
	print("Revoke User On Blockchain Network...")
	registered = 0
	c = zerorpc.Client()
	c.connect(blockChainAddress)
	c.Revoke(client_id)

def RegisterVerify(): 
	print("RegisterVerify on the call...")

def Verify(trx, leader_secret, proof): 
	#verify and append trx~
	print("verify in progress...")
	if leader_secret != proof:
		print("Verify Leader Failed! Trx not accepted!")
	else:
		commits.append(trx)

#********************* Message Handler Main Body ************************
class MSGHandler(object):
	def Distributor(self, endpoint, data):
		global client_id, current_trx
		print(endpoint + " - " + str(data))
		if endpoint == "Elect": 
			print("Hey I am the leader!!!")
			#safe to append and broadcast!
			commits.append(current_trx)
			broadcast(current_trx, client_id, client_id) #proof should come from Elect action. Skip the crypto part for now
			current_trx = {}
			#Revoke this round's registration
			Revoke()
			print("Transaction completed!")
		if endpoint == "Verify":
			received_data = json.loads(data)
			Verify(received_data[0], received_data[1], received_data[2])

def ear():
	s = zerorpc.Server(MSGHandler())
	s.bind("tcp://0.0.0.0" + ":" + str(client_port))
	s.run()

#create a thread to handle 'listening'
listen_thread = threading.Thread(target=ear, args=())
listen_thread.start()

while True: 
	text = input("")
	split = text.split()
	trx_id = randomId()

	if len(current_trx) != 0:
		print("Trx pending. Cannot accept new trx request.")
		continue

	if len(split) == 0: 
		continue
	elif len(split) == 2:
		balance = check_balance()

		if split[0] == client_name:
			print("Cannot transfer money to self!")
			continue
		if balance >= int(split[1]):
			current_trx = {
				"from":client_name, 
				"to":split[0], 
				"amt":int(split[1]), 
				"id": trx_id
				}
			if not Register():
				print("Election failed! Please Retry!")
				continue;
		else:
			print("Inefficient balance!")
	elif text == "show":
		pprint(commits)
	else: 
		print("Invalid Input here!")


