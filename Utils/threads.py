import threading
import asyncio
import traceback

class Mainframe(threading.Thread):
	""" thread starter, that runs all other modules and secures that they are running while active state """
	def __init__(self, BASE):
		super().__init__()
		self.BASE = BASE
		self.name = "Mainframe"
		self.loop = asyncio.new_event_loop()
		self.modules = dict(
			worker = dict(current=WorkerThread(BASE), tpl=WorkerThread)
		)

	def run(self) -> None:
		while self.BASE.Active.main:
			try:
				self.loop.run_until_complete(self.secureModules())

			except KeyboardInterrupt:
				break

			except Exception as e:
				self.BASE.Logger.critical(f"FATAL ERROR IN MAINFRAME SECURE LOOP: {str(e)}")

	async def secureModules(self) -> None:
		while self.BASE.Active.main:

			for module_name in self.modules:
				module = self.modules[module_name]["current"]

				if not module.isAlive():
					self.modules[module_name]["current"] = (self.modules[module_name]["tpl"])(self.BASE)
					self.modules[module_name]["current"].start()

			await asyncio.sleep(1)

class WorkerThread(threading.Thread):
	def __init__(self, BASE):
		super().__init__()
		self.BASE = BASE
		self.name = "Worker"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	async def sleepy(self):
		while 1: await asyncio.sleep(0.005)

	def run(self):
		try:

			asyncio.set_event_loop(self.loop)
			asyncio.ensure_future(self.sleepy())
			self.loop.run_forever()

		except Exception as e:
			self.BASE.Logger.critical(f"Worker Thread crashed: {str(e)}")
			traceback.print_exc()
