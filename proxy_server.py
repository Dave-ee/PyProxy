import socket, sys
from thread import *

ip_address = ''
ip_listen_port = 8001
ip_buffer_size = 4096
ip_max_conn = 5

def main():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((ip_address,ip_listen_port))
		s.listen(ip_max_conn)
		print("[INFO] Socket started")
		print("[INFO] IP: %s, Port: %s" % (str(s.getsockname()[0]), str(ip_listen_port)))
	except Exception, e:
		print("[FAIL] Failed to start socket server!")
		sys.exit(2)
	
	while 1:
		try:
			conn, addr = s.accept()
			data = conn.recv(ip_buffer_size)
			start_new_thread(connection,(conn,data,addr))
		except KeyboardInterrupt:
			s.close()
			print("[INFO] Proxy server shutting down..")
			sys.exit(1)
	s.close()
		
def connection(conn, data, addr):
	try:
		first_line = data.split('\n')[0]
		url = first_line.split(' ')[1]
		http_pos = url.find("://")
		if (http_pos==-1):
			temp = url
		else:
			temp = url[(http_pos+3):]
		
		port_pos = temp.find(":")
		webserver_pos = temp.find("/")
		if (webserver_pos==-1):
			webserver_pos = len(temp)
			
		webserver = ""
		port = -1
		if (port_pos==-1 or webserver_pos < port_pos):
			port = 80
			webserver = temp[:webserver_pos]
		else:
			port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
			webserver = temp[:port_pos]
		
		proxy(webserver,port,conn,data,addr)
	except Exception, e:
		print("[WARNING] Passed a connection from %s" % (str(addr[0])))
		pass

def proxy(webserver,port,conn,data,addr):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((webserver, port))
		s.send(data)
		while 1:
			reply = s.recv(ip_buffer_size)
			if (len(reply) > 0):
				conn.send(reply)
				dar = float(len(reply))
				dar = float(dar / 1024)
				dar = "%.3s" % (str(dar))
				dar = "%s KB" % (dar)
				print("[REQUEST] Client IP: %s, Data: %s" % (str(addr[0]),str(dar)))
			else:
				print("[WARNING] Broke a connection from %s to %s on port %s" % (str(addr[0]),webserver,str(port)))
				break
				
		s.close()
		conn.close()
	except socket.error, (value, message):
		print("[FAIL] Socket error found: %s" % message)
		s.close()
		conn.close()
		sys.exit(1)

main()