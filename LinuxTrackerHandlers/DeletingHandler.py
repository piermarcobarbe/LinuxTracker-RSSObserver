from Handler import Handler
from dotenv import load_dotenv

from os import unlink
from os.path import isfile
import logging

class DeletingHandler(Handler):

	def __init__(self, log_function):
		super().__init__(log_function)

	def handle(self, files, dry_run=False):
		for f in files:
			if isfile(f):
				self.log(logging.INFO, "Deleting file {}".format(f))
				unlink(f)

