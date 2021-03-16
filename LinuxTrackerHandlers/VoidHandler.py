from Handler import Handler
from dotenv import load_dotenv


class VoidHandler(Handler):
	def handle(self, files, dry_run=False):

		print("VoidHandler.handle()")
		print(files)

	def __init__(self):
		super().__init__()
		load_dotenv(verbose=True)
		print("Void handler initialized!")


