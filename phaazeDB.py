import time, os, sys, re, threading

file_lock = threading.Lock()

DB_FOLDER = "DATABASE"

class Dump(object):
	pass

def put(container, key, value):
	file_lock.acquire()

	print("adasdad")
	time.sleep(5)

	file_lock.release()

def get(container, key):
	pass

def save_data():
	threading.Timer(5.0, save_data).start()
	print('save Data')


#save_data()