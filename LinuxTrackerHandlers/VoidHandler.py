from Handler import Handler
from dotenv import load_dotenv


class VoidHandler(Handler):
	def handle(self, files, dry_run=False):
		print("=> Executing VoidHandler.handle()")
		print("This is VoidHandler.handle(), since it is a Void handler, we are doing nothing here :D")
		# print("files:", files)

	def __init__(self):
		super().__init__()
		load_dotenv(verbose=True)
		print("=> Void handler initialized!")
		print("This message is generated from the VoidHandler!")
		print("You can implement your own handler, the only thing you need is to override the 'handle' function.")
		print("In your handler, you will have as parameters the path of the files which have been generated, so it's")
		print("up to you what to do with such files.")


