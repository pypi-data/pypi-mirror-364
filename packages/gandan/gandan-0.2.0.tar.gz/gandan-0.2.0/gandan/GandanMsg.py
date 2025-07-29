#--*--coding:utf-8--*--
import struct, logging

class GandanMsg:
	seperator = b'!@#$'
	def __init__(self, pubsub, topic, data):
		if pubsub == 'PUB' or pubsub == 'P':
			self.pubsub = 'P'
		elif pubsub == 'SUB' or pubsub == 'S':
			self.pubsub = 'S'
		else:
			raise Exception('pubsub')
		self.topic_size = len(bytes(topic, "utf-8"))
		self.data_size = len(bytes(data,"utf-8"))
		(self.topic, self.data) = (topic, data)
		self.total_size = 0
		self.total_size = len(bytes(self))

	def __bytes__(self):
		_b = GandanMsg.seperator
		_b += bytes(self.pubsub, "utf-8")
		_b += struct.pack("!i", self.total_size)
		_b += struct.pack("!i", self.topic_size)
		_b += bytes(self.topic, "utf-8")
		_b += bytes(self.data, "utf-8")
		return _b
	
	def __str__(self):
		return self.topic+":"+self.data

	@staticmethod
	async def recv_async(reader):
		# b'#'까지 읽기
		_b = b''
		while True:
			_b += await reader.read(1)
			if len(_b) == 0:
				raise Exception('conn')
			if len(_b) >= 4:
				if _b[-4:] == GandanMsg.seperator:
					break
				else:
					raise Exception('sep')
				
		try:
			pubsub_byte = await reader.read(1)
			if len(pubsub_byte) < 1:
				raise Exception('timeout')
			pubsub = str(pubsub_byte, "utf-8")
			if pubsub != 'P' and pubsub != 'S':
				raise Exception('pubsub')

			total_size_byte = await reader.read(4)
			if len(total_size_byte) < 4:
				raise Exception('timeout')

			total_size = struct.unpack("!i", total_size_byte)[0]
			total_byte = await reader.read(total_size-9)
			topic_size = struct.unpack("!i", total_byte[0:4])[0]
			topic_bytes = total_byte[4:4+topic_size]
			topic = str(topic_bytes, "utf-8")
			data_bytes = total_byte[4+topic_size:]
			data = str(data_bytes, "utf-8")
		except Exception as e:
			raise Exception('convert total_size')
		
		logging.info("recv pubsub: %s, topic: %s, data: %s" % (pubsub, topic, data))

		return GandanMsg(pubsub, topic, data)

	@staticmethod
	def recv_sync(sock):
		"""
		동기 버전: reader는 socket 등 file-like 객체여야 하며, read(n) 메서드를 동기적으로 호출해야 합니다.
		"""
		_b = b''
		while True:
			_b += sock.recv(1)
			if len(_b) == 0:
				raise Exception('conn')
			if len(_b) >= 4:
				if _b[-4:] == GandanMsg.seperator:
					break
				else:
					raise Exception('sep')
		try:
			pubsub_byte = sock.recv(1)
			if len(pubsub_byte) < 1:
				raise Exception('conn')
			pubsub = str(pubsub_byte, "utf-8")
			if pubsub != 'P' and pubsub != 'S':
				raise Exception('pubsub')
 
			total_size_byte = sock.recv(4)
			if len(total_size_byte) < 4:
				raise Exception('conn')
 
			total_size = struct.unpack("!i", total_size_byte)[0]
			total_byte = sock.recv(total_size-9)
			topic_size = struct.unpack("!i", total_byte[0:4])[0]
			topic_bytes = total_byte[4:4+topic_size]
			topic = str(topic_bytes, "utf-8")
			data_bytes = total_byte[4+topic_size:]
			data = str(data_bytes, "utf-8")
		except Exception as e:
			raise Exception('convert total_size')
		logging.info("recv pubsub: %s, topic: %s, data: %s" % (pubsub, topic, data))
		return GandanMsg(pubsub, topic, data)