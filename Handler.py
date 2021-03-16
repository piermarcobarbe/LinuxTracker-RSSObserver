class Handler:

	def __init__(self, log_function):
		self._log_function = log_function

	def handle(self, files, dry_run=False):
		raise NotImplementedError()

	def log(self, log_level, message):
		self._log_function(log_level, message)

