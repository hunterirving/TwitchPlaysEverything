import sys
sys.dont_write_bytecode = True
import threading
import queue
import time
import vgamepad as vg
import re
import socket
import cfg
import os.path

buttons = ['u', 'd', 'l', 'r', 'a', 'b', 's']
gamepad = vg.VX360Gamepad()

q = queue.Queue()

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

s = socket.socket()
s.connect((cfg.HOST, cfg.PORT))
s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

os.system('clear')

print("Welcome to the chat room.\nNow playing POKEMON CRYSTAL.")

def sanitizeUserString(userString):
	return ''.join(userString.split()).lower()

def isCommand(sanitizedUserString):
	for char in sanitizedUserString:
		if char not in buttons:
			return False
	return True

def truncateCommand(command):
	return command[:10]

def process(un_and_m):
	sanitizedUserString = sanitizeUserString(un_and_m[1])
	if isCommand(sanitizedUserString):
		print(un_and_m[0] + ": ", end="")
		sys.stdout.flush()
		pressKeys(truncateCommand(sanitizedUserString))

def pressKeys(truncatedCommandString):
	for char in truncatedCommandString:
		print(char + " ", end="")
		sys.stdout.flush()
		if char == 'a':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
		elif char == 'b':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
		elif char == 'u':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)	
		elif char == 'd':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
		elif char == 'l':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
		elif char == 'r':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
		elif char == 's':
			gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
		gamepad.update()
		time.sleep(0.1)
		gamepad.reset()
		gamepad.update()
		time.sleep(0.5)
	print('\n')

def listen():
	response = s.recv(1024).decode("utf-8")
	if response == "PING :tmi.twitch.tv\r\n":
		s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
	else:
		username = re.search(r"\w+", response).group(0)
		message = CHAT_MSG.sub("", response)
		message = message[:-2]
		q.put([username, message])

def listener():
	while True:
		listen()
		pass

def worker():
	while True:
		un_and_m = q.get()
		process(un_and_m)
		q.task_done()

threading.Thread(target=listener, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()

while True:
	q.join()
