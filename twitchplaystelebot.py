import threading
import queue
import time
import re
import socket
import cfg
import os.path
import sys
import pyttsx3
sys.dont_write_bytecode = True

engine = pyttsx3.init()

q = queue.Queue()

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

os.system('clear')

print("Welcome to SINGULARITY NOW. You are currently inhabiting TELEBOT.")

def listen():
	response = s.recv(1024).decode("utf-8")
	if response == "PING :tmi.twitch.tv\r\n":
		s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
	else:
		username = re.search(r"\w+", response).group(0)
		message = CHAT_MSG.sub("", response)
		message = message[:-2]
		if not message.startswith(":tmi.twitch.tv") and not message.startswith(":pythonchatbot"):
			q.put([username,message])

def listener():
	while True:
		listen()
		pass

def worker():
	while True:
		un_and_m = q.get()
		engine.say(un_and_m[1])
		engine.runAndWait()
		q.task_done()

threading.Thread(target=listener, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()

while True:
	q.join()
