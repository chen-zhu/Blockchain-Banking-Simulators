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
import numpy as np
from pprint import pprint
from Lib.helper import *

lock = threading.Lock()

#argv client_id, client_name, port_lowerRange, port_upperRange

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

current_trx = {}
start_time = time.time()
paxos_runing_flag = 0

request_num = np.random.randint(low=1, high=10)
BallotNum = 0
acc_num = 0 #accepted request num --> request_num * 10 + id!
acc_val = 0

receive_ack = []
initial_val = ""
receive_accpeted = []
leader_pick = ""
start_time = time.time()

print("Majority: " + str(((port_upperRange - port_lowerRange) // 2) + 1) + ". request_num: " + str(request_num))
print("client id: " + str(client_id) + ". client name: " + str(client_name))

#*********************BlockcChain Main Body Function************************
id_maps = []
commits = []

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

def broadcast_msg(endpoint, data): 
	global port_lowerRange, port_upperRange, client_port
	for i in range(port_lowerRange, port_upperRange + 1): 
		#do not broadcast to self!
		if str(i) == str(client_port):
			continue;
		c = zerorpc.Client(heartbeat=None)
		c.connect("tcp://0.0.0.0:" + str(i))
		c.Distributor(endpoint, data)
		c.close()

#********************* Modified Paxos Leader Election ************************
def majority_detected(type):
	global receive_ack, port_upperRange, port_lowerRange
	majority_num = ((port_upperRange - port_lowerRange) // 2) + 1

	if type == "promise":
		if len(receive_ack) >= majority_num: 
			return True
		else: 
			return False


def Prepare(): 
	global request_num, client_id, BallotNum, client_name, paxos_runing_flag, lock, initial_val
	lock.acquire()
	paxos_runing_flag = 1
	request_num += 1
	BallotNum = request_num * 100000 + int(client_id)
	msg_body = {
		"request_num": request_num,
		"owner_id": client_id, 
		"BallotNum": BallotNum, 
	}
	initial_val = client_name
	lock.release()
	broadcast_msg("ReceivePrepare", json.dumps(msg_body))

def Promise(data):
	global commits, request_num, client_id, BallotNum
	global acc_num, acc_val, lock
	received = json.loads(data)
	if received["BallotNum"] >= BallotNum:
		lock.acquire()
		request_num = received["request_num"]
		BallotNum = received["BallotNum"]
		msg_body = {
			"type": "promise",
			"BallotNum": BallotNum, 
			"request_num": request_num,
			"acc_num": acc_num, 
			"acc_val": acc_val,
		}
		lock.release()
		c = zerorpc.Client(heartbeat=None)
		c.connect("tcp://0.0.0.0:" + str(received['owner_id']))
		c.Distributor("ReceivePromise", json.dumps(msg_body))
		c.close()
	else:
		msg_body = {
			"type": "rej",
			"request_num": request_num,
			"BallotNum": BallotNum,
		}
		c = zerorpc.Client(heartbeat=None)
		c.connect("tcp://0.0.0.0:" + str(received['owner_id']))
		c.Distributor("ReceiveRejection", json.dumps(msg_body))
		c.close()

def Accept(): 
	global receive_ack, initial_val, request_num, BallotNum, lock, leader_pick
	myVal = ""

	vals = []
	val_with_highest_req_num = ""
	highest_req_num = 0
	send_req_num = 0

	for ack in receive_ack: 
		if (not ack["acc_val"] == 0):
			vals.append(ack["acc_val"])
		if (not ack["acc_val"] == 0) and highest_req_num < ack["acc_num"]: 
			val_with_highest_req_num = ack["acc_val"]
			highest_req_num = ack["BallotNum"]
			send_req_num = ack["request_num"]

	lock.acquire()
	if len(vals) == 0: 
		myVal = initial_val
		send_req_num = request_num
	else: 
		myVal = val_with_highest_req_num

	msg_body = {
		"type": "accept", 
		"request_num": send_req_num, 
		"BallotNum": BallotNum,
		"value": myVal
	}

	lock.release()
	leader_pick = myVal
	print("[ACCEPT] >>> Final Leader Chosen: " + myVal)
	broadcast_msg("ReceiveAccept", json.dumps(msg_body))

#This accepted function is wrong. it does not obey Paxos workflow!
def Accepted(): 
	global current_trx, commits, id_maps, start_time
	if len(current_trx) > 0: 
		commits.append(current_trx)
		id_maps.append(current_trx['id'])
		broadcast_msg("Commit", json.dumps(current_trx))
		current_trx = []
		print("Transaction Completed. " + " [Total Benchmark:] " + str(time.time() - start_time) + " seconds")

def Commits(data): 
	global leader_pick, commits, current_trx
	received = json.loads(data)
	if len(received) > 0: 
		lock.acquire()
		id_maps.append(received['id'])
		commits.append(received)
		current_trx = []
		print("Transaction appended [Total Benchmark:] " + str(time.time() - start_time) + " seconds")
		lock.release()


#********************* Message Handler Main Body ************************
class MSGHandler(object):
	def Distributor(self, endpoint, data):
		global client_id, current_trx, lock, start_time, receive_ack, leader_pick, client_name
		print("[DEBUG] - Endpoint: " + endpoint + ", Data: " + str(data))
		if endpoint == "ReceivePrepare": 
			#do promise here~
			Promise(data)
		elif endpoint == "ReceivePromise":
			receive_ack.append(json.loads(data))
			if majority_detected("promise"):
				Accept()
				receive_ack = [] #reset receive_ack~
				if leader_pick == client_name:
					Accepted()
		elif endpoint == "ReceiveRejection":
			print("ReceiveRejection")
		elif endpoint == "ReceiveAccept":
			leader_pick = json.loads(data)['value']
			print("ReceiveAccept Leader now is " + json.loads(data)['value'])
		elif endpoint == "Commit":
			print('Commit --- ' + data)
			Commits(data)

def ear():
	s = zerorpc.Server(MSGHandler(), pool_size=1000, heartbeat=None)
	s.bind("tcp://0.0.0.0" + ":" + str(client_port))
	s.run()

#create a thread to handle 'listening'
listen_thread = threading.Thread(target=ear, args=())
listen_thread.start()

def inputHandler(text): 
	global current_trx, client_name, commits
	split = text.split()
	trx_id = randomId(15)

	if len(split) == 0: 
		return False
	elif len(split) >= 2:
		balance = check_balance()

		if split[0] == client_name:
			print("Cannot transfer money to self!")
			return False
		if balance >= int(split[1]):
			current_trx = {
				"from": client_name, 
				"to": split[0], 
				"amt":int(split[1]), 
				"id": split[2] if (len(split) >= 2) else trx_id
				}
			Prepare()
		else:
			print("Inefficient balance!")
			return True
	elif split[0] == "show":
		pprint(commits)
		print(str(request_num) + " - " + str(BallotNum) + " - " + str(len(commits)) + ". On Map: " + str(len(id_maps)))
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
		line_count = 0
		for line in f_stream:
			line_count += 1
			id = line.split()[2]
			while not (id in id_maps):
				#keep retrying until this proposal goes through
				inputHandler(line)
				time.sleep(0.5)
			print("PROCESSED LINE: " + str(line_count))

while True: 
	text = input("")
	inputHandler(text)














