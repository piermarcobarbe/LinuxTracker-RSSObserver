from Handler import Handler
from transmission_rpc import Client
from dotenv import load_dotenv
from os import getenv
from json import dumps
from sys import exit


class TransmissionHandler(Handler):

	def __init__(self):
		super().__init__()
		load_dotenv(verbose=True)
		self.host = getenv("TRANSMISSION_HOST") or "localhost"
		self.port = getenv("TRANSMISSION_PORT") or 9091
		self.username = getenv("TRANSMISSION_USERNAME") or "transmission"
		self.password = getenv("TRANSMISSION_PASSWORD") or "password"
		try:
			self.client = Client(
				host=self.host,
				port=self.port,
				username=self.username,
				password=self.password
			)
			print("Connected to {}:{}".format(self.host, self.port))
		except Exception as e:
			print("Cannot connect to {}@{}:{}".format(self.username, self.host, self.port))
			print(e)
			exit(1)

	def handle(self, files, dry_run=False):

		if not dry_run:
			for f in files:
				self.add_torrent(f)
		else:
			print("Not adding files since dry run mode is activated.")

	def as_dict(self):
		data = self.__dict__.copy()
		del data['client']
		return data

	def __str__(self):
		return dumps(self.as_dict(), indent=4)

	def add_torrent(self, torrent_path):
		with open(torrent_path, 'rb') as fp:
			try:
				self.client.add_torrent(fp)
				print("Added torrent file {}".format(torrent_path))
			except:
				print("Cannot add {}".format(torrent_path))
