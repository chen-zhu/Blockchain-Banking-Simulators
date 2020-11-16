import random
import string
import numpy as np

port_lowerRange = 50000
port_upperRange = 50009
log_sizePerClient = 500

fake_clientName = []

for i in range(port_lowerRange, port_upperRange + 1):  
	fake_clientName.append(''.join(random.choice(string.ascii_uppercase) for i in range(5)))

for f_c in fake_clientName:
	log_count = 0;
	generated_fileName = f_c + "_" + str(port_lowerRange)
	port_lowerRange += 1

	print("FileName: " + generated_fileName)
	f = open("Raw/" + generated_fileName, "w")
	while log_count <= log_sizePerClient: 
		rand_trx_val = np.random.randint(low=1, high=10)
		rand_trx_client = random.choice(fake_clientName)
		if rand_trx_client == f_c:
			continue
		else:
			log_count += 1
			log = rand_trx_client + " " + str(rand_trx_val) + "\n"
			f.write(log)
	f.close()

