import random
import string
import pathlib
import time
import os
import numpy as np

port_lowerRange = 50000
port_upperRange = 50009
log_sizePerClient = 50

fake_clientName = []

print("\n>>> Deleting old raw data files...")
data_path = str(pathlib.Path().absolute()) + "/Raw/"
for file_name in os.listdir(data_path): 
	if file_name == ".DS_Store":
		continue
	elif os.path.exists(data_path + file_name):
		os.remove(data_path + file_name)
		print("Deleted raw file: " + file_name)
time.sleep(2)

print("\n[Current settings: port_lowerRange", port_lowerRange, ", port_upperRange", port_upperRange, ", log_sizePerClient", log_sizePerClient, "]\n")

print(">>> Generating new raw data files...")
for i in range(port_lowerRange, port_upperRange + 1):  
	fake_clientName.append(''.join(random.choice(string.ascii_uppercase) for i in range(5)))

for f_c in fake_clientName:
	log_count = 0;
	generated_fileName = f_c + "_" + str(port_lowerRange)
	port_lowerRange += 1

	print("Generated raw file: " + generated_fileName)
	f = open("Raw/" + generated_fileName, "w")
	while log_count < log_sizePerClient: 
		rand_trx_val = np.random.randint(low=1, high=10)
		rand_trx_client = random.choice(fake_clientName)
		if rand_trx_client == f_c:
			continue
		else:
			log_count += 1
			log = rand_trx_client + " " + str(rand_trx_val) + " " + ''.join(random.choice(string.ascii_lowercase) for i in range(15)) + "\n"
			f.write(log)
	f.close()

