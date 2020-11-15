import xml.etree.ElementTree as ET
import socket
import sys
import json
import copy
import random
import string
import time
import copy
import threading
import os



def randomId(stringLength=5):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))