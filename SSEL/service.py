import sys
import json
import copy
import random
import string
import time
import copy
import threading
import zerorpc
import pathlib
from pprint import pprint
from Lib.helper import *

lock = threading.Lock()

#Filename if given, it will override client_id and client_name!!!!
benchmark_file = sys.argv[5] if (len(sys.argv) > 5) else ""

if len(benchmark_file) > 0: 
	split = benchmark_file.split("_")
	client_name = split[0]
	client_id = split[1]
else:
	client_id = sys.argv[1]
	client_name = sys.argv[2]

client_port = client_id
client_ip = "tcp://127.0.0.1"

port_lowerRange = int(sys.argv[3])
port_upperRange = int(sys.argv[4])

registered = 0
current_trx = {}
start_time = time.time()

#*********************BlockcChain Main Body Function************************
genesis = []
commits = []
blockChainAddress = "tcp://127.0.0.1:5000"

def check_balance():
	initial_balance = 100000
	global genesis, commits, client_name
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
		c.close()


#********************* Single Secret Leader Election ************************
def Register(): 
	global registered, blockChainAddress, client_id, client_name, genesis
	print(">>> REGISTER User On Blockchain Network...")
	registered = 1
	c = zerorpc.Client()
	c.connect(blockChainAddress)
	ret = c.Register(client_id, client_name, len(genesis) + 1)
	c.close()
	return True if (ret == 1) else False

def Revoke():
	global registered, blockChainAddress, client_id, client_name, genesis
	print(">>> REVOKE User On Blockchain Network...")
	registered = 0
	c = zerorpc.Client()
	c.connect(blockChainAddress)
	c.Revoke(client_id)
	c.close()

def RegisterVerify(): 
	print(">>> RegisterVerify on the call...")

def Verify(trx, leader_secret, proof): 
	#verify and append trx~
	global lock, start_time
	print("<<< VERIFY in progress...")
	if leader_secret != proof:
		print("Verify Leader Failed! Trx not accepted!")
	else:
		lock.acquire()
		commits.append(trx)
		print("<<< Transaction accepted! Current Balance: " + str(check_balance()) + " [Total Benchmark:] " + str(time.time() - start_time) + " seconds")
		lock.release()

#********************* Message Handler Main Body ************************
class MSGHandler(object):
	def Distributor(self, endpoint, data):
		global client_id, current_trx, lock, start_time
		print("[DEBUG] - Endpoint: " + endpoint + ", Data: " + str(data))
		if endpoint == "Elect": 
			lock.acquire()
			print("<<< Hey I am the leader!!!")
			#safe to append and broadcast!
			commits.append(current_trx)
			broadcast(current_trx, client_id, client_id) #proof should come from Elect action. Skip the crypto part for now
			current_trx = {}
			#Revoke this round's registration
			Revoke()
			print("Transaction completed! [Total Benchmark:] " + str(time.time() - start_time) + " seconds")
			lock.release()
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

def inputHandler(text): 
	global current_trx, client_name, commits
	split = text.split()
	trx_id = randomId(15)

	if len(current_trx) != 0:
		print("Trx pending. Cannot accept new trx request. < " + text)
		return False

	if len(split) == 0: 
		return False
	elif len(split) == 2:
		balance = check_balance()

		if split[0] == client_name:
			print("Cannot transfer money to self!")
			return False
		if balance >= int(split[1]):
			current_trx = {
				"from":client_name, 
				"to":split[0], 
				"amt":int(split[1]), 
				"id": trx_id
				}
			if not Register():
				print("Election failed! Please Retry!")
				return False
		else:
			print("Inefficient balance!")
			return True
	elif split[0] == "show":
		pprint(commits)
		return True
	elif split[0] == "balance":
		print("Current Balance: " + str(check_balance()))
		return True
	else: 
		print("Invalid Input here!")
		return True

if len(benchmark_file) != 0: 
	data_path = str(pathlib.Path().absolute()) + "/../Data/Raw/" + benchmark_file
	with open(data_path) as f_stream:
		for line in f_stream:
			while len(current_trx) != 0:
				time.sleep(0.1)
			inputHandler(line)

while True: 
	text = input("")
	inputHandler(text)







