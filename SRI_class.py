''' set the ipv4 addrress as 192.168.0.2 and 255.255.255.0'''
import numpy as np
import struct
import socket

class sunrise():
	def __init__(self):
		self.IP_ADDR = '192.168.0.108'
		self.PORT = 4008
		#创建连接插口
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			#连接
			self.s.connect((self.IP_ADDR, self.PORT))
			self.ok = True
			print('sri ok')
		except:
			self.ok =False
			print('sri error')
			return
		
		# 采样频率
		set_update_rate = "AT+SMPR=1000\r\n"
		self.s.send(set_update_rate.encode())
		recvData = bytearray(self.s.recv(1000))
		# print('采样频率', recvData)
		
		# 上传数据格式
		set_recieve_format = "AT+SGDM=(A01,A02,A03,A04,A05,A06);E;1;(WMA:1)\r\n"
		self.s.send(set_recieve_format.encode())
		recvData = bytearray(self.s.recv(1000))
		# print(recvData)
		
	def enable(self):
		if self.ok == True:
			# 连续上传数据包
			get_data_stream = "AT+GSD\r\n"
			self.s.send(get_data_stream.encode())
			print('Sunrise enable')
		else:
			print('no sunrise found, failed to enable')
	def rec(self):
		if self.ok == True:
			data = self.s.recv(1000)
			fx = struct.unpack("f", data[6:10])[0]
			fy = struct.unpack('f', data[10:14])[0]
			fz = struct.unpack('f', data[14:18])[0]
			mx = struct.unpack('f', data[18:22])[0]
			my = struct.unpack('f', data[22:26])[0]
			mz = struct.unpack('f', data[26:30])[0]
			F = np.array([fx, fy, fz, mx, my, mz])
			return F
	def disable(self):
		if self.ok == True:
			stop_data_stream = "AT+GSD=STOP\r\n"
			self.s.send(stop_data_stream.encode())
			print('Sunrise disable ')

