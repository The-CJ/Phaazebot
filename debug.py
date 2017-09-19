#BASE.moduls.debug

import asyncio
import tkinter as tk

class Deb():
	def  __init__(self, BASE):
		self.BASE = BASE
		self.root = tk.Tk()

		self.root.title("PhaazeOS System Debug")

		self.storage = None
		self.last_operation = ""
		self.async_operation = tk.IntVar()
		self.output = tk.StringVar()
		self.return_value = tk.StringVar()

		self.frame = tk.Frame(self.root)
		self.lable_site = tk.Label(self.root, text="root@phaazeos >>>").grid(row=2, column=0, sticky="E")
		self.lable_down = tk.Label(self.root, textvariable=self.output,justify='left').grid(row=0, column=1, sticky="W")
		self.entry = tk.Entry(self.root, width=40, textvariable=self.storage, justify='left').grid(row=2, column=1, sticky="W")
		self.result = tk.Label(self.root, textvariable=self.return_value, justify='left', fg="blue", wraplength=500).grid(row=3, column=1, sticky="W")

		self.async_box = tk.Checkbutton(self.root, text="Async operation:", variable=self.async_operation).grid(row=1, sticky="E")

		self.root.bind("<Return>", func=self.Return_)
		self.root.bind("<Up>", func=self.load_last)
		self.root.mainloop()

	def load_last(self, event):
		event.widget.delete(0, 'end')
		event.widget.insert(0, self.last_operation)

	def Return_(self, event):
		command = event.widget.get()
		event.widget.width = 50
		self.output.set(self.output.get() + "\n>> " + command)
		self.output.set(self.output.get()[-200:])
		event.widget.delete(0, 'end')

		if command == "clear":
			self.output.set("")
			self.return_value.set("Cleared")
			return

		elif command == "shutdown":
			loop = asyncio.new_event_loop()
			loop.run_until_complete(self.BASE.shutdown(self.BASE))
			return exit()

		elif command == "reload":
			loop = asyncio.new_event_loop()
			loop.run_until_complete(self.BASE.utils.reload_(self.BASE))

		try:
			self.last_operation = command

			if self.async_operation.get() == 1:
				loop = asyncio.new_event_loop()
				f = asyncio.ensure_future(eval(command))
				self.result = tk.Label(self.root, textvariable=self.return_value, justify='left', fg="lime", wraplength=500).grid(row=3, column=1, sticky="W")
			else:
				f = eval(command)
				self.result = tk.Label(self.root, textvariable=self.return_value, justify='left', fg="blue", wraplength=500).grid(row=3, column=1, sticky="W")

			self.return_value.set(f)
		except Exception as Fail:
			self.result = tk.Label(self.root, textvariable=self.return_value, justify='left', fg="red", wraplength=500).grid(row=3, column=1, sticky="W")
			self.return_value.set(str(Fail))


async def main(BASE):
	Deb(BASE)
