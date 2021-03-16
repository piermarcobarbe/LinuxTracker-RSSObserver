from Handler import Handler
from dotenv import load_dotenv

from logging import INFO

class VoidHandler(Handler):
	def handle(self, files, dry_run=False):
		self.log(INFO, "=> Executing VoidHandler.handle()")
		self.log(INFO, "This is VoidHandler.handle(), since it is a Void handler, we are doing nothing here :D")
		# print("files:", files)

	def __init__(self, log_function):
		super().__init__(log_function)
		load_dotenv(verbose=True)
		self.log(INFO, "=> Void handler initialized!")
		self.log(INFO, "This message is generated from the VoidHandler!")
		self.log(INFO, "You can implement your own handler, the only thing you need is to override the 'handle' function.")
		self.log(INFO, "In your handler, you will have as parameters the path of the files which have been generated, so it's")
		self.log(INFO, "up to you what to do with such files.")


