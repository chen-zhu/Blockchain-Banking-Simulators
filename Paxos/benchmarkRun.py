import time
import os
import pathlib
from pprint import pprint

data_path = str(pathlib.Path().absolute()) + "/../Data/Raw/"
print(data_path)
arr = os.listdir(data_path)

size_check = len(arr)
if '.DS_Store' in arr: 
	size_check -= 1

port_lowerRange = "50000"
port_upperRange = str(int(port_lowerRange) + size_check - 1)

#*****Run Client Servers *****
for file_name in os.listdir(data_path): 
	if file_name == ".DS_Store":
		continue
	print(file_name)
	command = "osascript -e 'tell application \"Terminal\" to do script \"cd " + str(pathlib.Path().absolute()) + " && python3 ./service.py DUMMYID DYMMYNAME " + port_lowerRange + " " + port_upperRange + " " + file_name + " \"' "
	os.system(command)