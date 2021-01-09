from Handler import Handler


class PrintingHandler(Handler):
	def handle(self, files):
		print(self.__class__)
		for f in files:
			print(f)
