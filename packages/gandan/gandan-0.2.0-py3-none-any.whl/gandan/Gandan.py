#--*--coding=utf-8--*--
import sys, re, logging, traceback, asyncio
from os import path
import re, threading, logging
import hashlib, base64, json
import asyncio

try:
	from .GandanMsg import *
	from .MMAP  import *
except Exception as e:
	from gandan.GandanMsg import *
	from gandan.MMAP  import *

class Gandan:
	def __init__(self, ip_port, debug=False):
		self.ip_port = ip_port

		self.sub_topic = {}
		self.sub_topic_lock = asyncio.Lock()

	@staticmethod
	def setup_log(path, level = logging.DEBUG):
		l_format = '%(asctime)s:%(msecs)03d^%(levelname)s^%(funcName)20s^%(lineno)04d^%(message)s'
		d_format = '%Y-%m-%d^%H:%M:%S'
		logging.basicConfig(filename=path, format=l_format, datefmt=d_format,level=level)

	@staticmethod
	def error_stack(stdout = False):
		_type, _value, _traceback = sys.exc_info()
		logging.info("#Error" + str(_type) + str(_value))
		for _err_str in traceback.format_tb(_traceback):
			if stdout == False:
				logging.info(_err_str)
			else:
				logging.info(_err_str)
				
	@staticmethod
	def version():
		return int(re.sub('\.','',sys.version.split(' ')[0][0]))

	async def handler(self, reader, writer):
		addr = writer.get_extra_info('peername')
		logging.info("addr : %s" % str(addr))
		while(True):
			try:
				msg = await GandanMsg.recv_async(reader)
				logging.info("data : %s" % str(msg))

				if msg.pubsub == 'P':
					try:
						async with self.sub_topic_lock:
							if msg.topic in self.sub_topic:
								remove_writers = []
								for sub_writer in self.sub_topic[msg.topic]:
									try:
										sub_writer.write(bytes(msg))
										await sub_writer.drain()
									except Exception as e:
										logging.info(f"writer error: {e}")
										remove_writers.append(sub_writer)
								# 에러난 writer 제거
								for w in remove_writers:
									if w in self.sub_topic[msg.topic]:
										self.sub_topic[msg.topic].remove(w)
					except Exception as e:
						logging.info(f"lock or pub error: {e}")
				elif msg.pubsub == 'S':
					try:
						logging.info("sub topic: %s" % msg.topic)
						async with self.sub_topic_lock:
							if msg.topic not in self.sub_topic:
								self.sub_topic[msg.topic] = [writer]
							else:
								if writer not in self.sub_topic[msg.topic]:
									self.sub_topic[msg.topic].append(writer)
					except Exception as e:
						logging.info(f"lock or sub error: {e}")
			except Exception as e:
				logging.info("error : %s" % str(e))
				break

	# start를 asyncio 기반으로 변경
	async def start(self):
		async def client_connected_cb(reader, writer):
			await self.handler(reader, writer)

		server = await asyncio.start_server(
			client_connected_cb,
			self.ip_port[0], self.ip_port[1]
		)
		logging.info("------------ MW Gandan Version[%d] Start --------------" % Gandan.version())
		async with server:
			await server.serve_forever()
