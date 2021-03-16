from Handler import Handler
from dotenv import load_dotenv

from os import unlink
from os.path import isfile

class DeletingHandler(Handler):
	def handle(self, files, dry_run=False):
		for f in files:
			if isfile(f):
				print("Deleting file {}".format(f))
				unlink(f)

	def __init__(self):
		super().__init__()
