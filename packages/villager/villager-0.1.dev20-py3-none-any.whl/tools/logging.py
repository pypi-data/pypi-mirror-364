import datetime
import functools
import json
import os
from typing import List
import orjson


# 日志对象,用来在各个中间件之间传递日志信息
class Logging(object):
	def __init__(self, level, data):
		self.level = level
		self.data = data
		self.logging_time = datetime.datetime.now().isoformat()

	def __dict__(self):
		return {
			"level": self.level,
			"data": self.data,
			"logging_time": self.logging_time,
		}


# 在送到输出流之前的日志对象用于在各个中间件中以字符串的视角对日志进行处理
class Preflush:
	def __init__(self, data_object: Logging, data_str: str):
		self.data_object: Logging = data_object
		self.data_str: str = data_str


# 日志中间件的抽象类
class LoggingMiddlewareAbstract(object):
	# 处理Object形式的日志的函数
	def write(self, data: Logging) -> Logging:
		raise NotImplementedError()

	# 处理str形式的日志的函数
	def flush(self, data: Preflush) -> Preflush:
		raise NotImplementedError()




# 将日志处理成json序列化字符串的方式的中间件
class JsonLoggingMiddleware(LoggingMiddlewareAbstract):
	def write(self, data: Logging) -> Logging:
		return data

	def flush(self, data: Preflush) -> Preflush:
		print(data)
		def default(obj):
			return "<class '{}'>".format(type(obj))
		#data.data_str = orjson.dumps(data.data_object.__dict__(), default=default, option=orjson.OPT_SERIALIZE_NUMPY).decode()
		data.data_str = json.dumps(data.data_object.__dict__(), ensure_ascii=False, default=str) + "\n"

		return data


# 抽象的日志输出流
class AbstractLoggingStream:
	def write(self, data: str) -> Logging:
		raise NotImplementedError()


# 日志输出到终端的流
class LoggingToConsole(AbstractLoggingStream):
	def write(self, data: str):
		logging_time = datetime.datetime.now().isoformat()
		print(f"[DEBUG] time:{logging_time} data:{data}")


# 日志输出到文件的流
class LoggingToFile(AbstractLoggingStream):
	def __init__(self, filename="function_log.json"):
		self.filename = filename
		self.fs = open(self.filename, "a")

	def write(self, data: str):
		self.fs.write(f"{data}\n")
		self.fs.flush()

"""
/**
	问AI
*/
"""


# 日志的具体实现,这个日志是在整个进程中为单例的
class __logging:
	def __init__(self):
		self._logging_stream: AbstractLoggingStream = LoggingToConsole()
		self._check_logging_level()
		self._loging_level: int = 0
		self._logging_middleware: List[LoggingMiddlewareAbstract] = list()
		self._logging_middleware.append(JsonLoggingMiddleware())

	def _check_logging_level(self):
		self._loging_level = int(os.environ.get("LOGGING_LEVEL", 0))

	def set_logging_level(self, level: int):
		self._loging_level = level

	def set_logging_middleware(self, middleware: List[LoggingMiddlewareAbstract]):
		self._logging_middleware = middleware

	def set_logging_stream(self, logging_stream: AbstractLoggingStream):
		self._logging_stream = logging_stream

	def _log(self, data: Logging):
		if data.level < self._loging_level < 0:
			del data
			return
		for middleware in self._logging_middleware:
			data = middleware.write(data)

		pre_flush = Preflush(data_object=data, data_str="")

		for middleware in self._logging_middleware:
			pre_flush = middleware.flush(pre_flush)

		self._logging_stream.write(pre_flush.data_str)

	# 普通日志
	def log(self, data, logging_level: int = 0):
		self._log(Logging(level=logging_level, data=data))

	# 用于监控函数输入输出的装饰器
	def function_logging(self, logging_level: int = 0):
		def decorator(func):
			@functools.wraps(func)
			def wrapper(*args, **kwargs):
				try:
					result = func(*args, **kwargs)
					status = "Success"
					error = None
				except Exception as e:
					result = None
					status = "Error"
					error = e
				log_data = {
					"function_name": func.__name__,
					"arguments": {
						"args": args,
						"kwargs": kwargs
					},
					"status": status,
					"return_value": result,
					"error": str(error)
				}
				self._log(Logging(level=logging_level, data=log_data))
				if error is not None:
					raise error
				return result

			return wrapper

		return decorator


logging = __logging()
