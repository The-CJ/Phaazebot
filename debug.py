#BASE.moduls.debug

import asyncio
import tkinter as tk

class Deb():
	def  __init__(self, BASE):
		self.BASE = BASE
		self.root = tk.Tk()

		self.root.title("Test")
		#self.root.geometry("300x150")
		self.storage = None

		self.frame = tk.Frame(self.root)
		self.lable = tk.Label(self.root, text=">>>").pack(side=tk.LEFT)
		self.entry = tk.Entry(self.root, textvariable=self.storage).pack(side=tk.RIGHT)
		self.root.bind("<Return>", func=self.Return_)

		self.frame.pack()
		self.root.mainloop()

	def Return_(self, event):
		print(event.widget.get())
		event.widget.delete(0, 'end')

async def main(BASE):
	Deb(BASE)

l = asyncio.new_event_loop()
l.run_until_complete(main())