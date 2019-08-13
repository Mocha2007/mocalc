from math import acos, asin, atan, cos, exp, factorial, gamma, gcd, log, sin, tan
from cmath import acos as cacos, asin as casin, atan as catan, cos as ccos, exp as cexp, log as clog, sin as csin, tan as ctan
from random import random
from time import sleep
from copy import deepcopy
import sys
import tkinter as tk
from _tkinter import TclError
# ty https://www.python-course.eu/tkinter_buttons.php <3
# https://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm

digits = '0123456789'
keys = [
	['~', 'sqrt', 'square', '^', '←', '', 'abs', 'gcd'],
	['7', '8', '9', '/', '', ';', 'rand', 'ln', 'hypot'],
	['4', '5', '6', '*', '', '.', '!', 'sin', 'asin'],
	['1', '2', '3', '-', '', '@', 'exp', 'cos', 'acos'],
	['', '', '%', '+', '', '\\', 'mod', 'tan', 'atan'],
]
shortcuts = {
	'<Return>': '↵',
	'<BackSpace>': '←',
	'<Delete>': 'clear',
	'<Key-0>': '0',
	'#': 'rand',
	'&': 'and',
	'C': 'acos',
	'S': 'asin',
	'T': 'atan',
	'a': 'abs',
	'c': 'cos',
	'e': 'exp',
	'g': 'gcd',
	'h': 'hypot',
	'l': 'ln',
	'm': 'mod',
	'n': 'not',
	'q': 'square',
	'r': 'sqrt',
	's': 'sin',
	't': 'tan',
	'x': 'xor',
	'|': 'or',
}
buttons = deepcopy(keys)
programmer_keys = deepcopy(keys)
programmer_keys[0] = 'not and or xor ←'.split()
key_coords = {}
for i, row in enumerate(keys):
	for j, k in enumerate(row):
		key_coords[k] = i, j

# set up vars

stack = [0]
history = []

# functions

def error(name: str='Error'):
	print(name)
	screen.config(text=name, bg='red')
	root.update()
	sleep(1)
	numpad('clear')


def numpad(n: str):
	global history
	global stack
	# try:
		# print(n)
	# except UnicodeEncodeError:
		# print('...')
	history.append(n)
	# easy errors
	if n in {'acos', 'asin'} and not (-1 <= stack[-1] <= 1):
		return error('DomainError')
	elif n in {'cos', 'sin', 'tan'} and 2**2**9 < abs(stack[-1]):
		return error('OverflowError')
	# main
	if n in digits: # 48-57
		n = int(n)
		stack[-1] *= 10
		stack[-1] += -n if n < 0 else n
	# speshul
	elif n == 'clear':
		stack = [0]
		history = []
	elif n in {'↵', '=', 'enter', 'return'}:
		stack.append(0)
	# other than special
	elif n == '!': # 33
		if isinstance(stack[-1], int) and 0 <= stack[-1] < 2**31:
			stack[-1] = factorial(stack[-1])
		else:
			try:
				stack[-1] = gamma(stack[-1] + 1)
			except ValueError:
				error('DomainError')
			except OverflowError:
				error('OverflowError')
	elif n == '$': # 36
		index = stack.pop()
		if isinstance(index, int):
			if len(stack) and abs(index) <= len(stack):
				stack.append(stack[index])
			else:
				error('IndexError')
		else:
			error('TypeError')
	elif n == '%': # 37
		if 1 < len(stack):
			stack.append(stack[-2] * stack.pop()/100)
		else:
			stack[-1] = 0
	elif n == '*': # 42
		if 1 < len(stack):
			stack.append(stack.pop() * stack.pop())
		else:
			stack[-1] = 0
	elif n == '+': # 43
		if 1 < len(stack):
			stack.append(stack.pop() + stack.pop())
	elif n == '-': # 45
		if 1 < len(stack):
			stack.append(stack.pop(-2) - stack.pop())
		else:
			stack[-1] *= -1
	elif n == '.': # 46
		stack.append(stack[-1])
	elif n == '/': # 47
		if 1 < len(stack):
			if stack[-1]:
				if idiv:
					stack.append(stack.pop(-2) // stack.pop())
				else:
					stack.append(stack.pop(-2) / stack.pop())
			else:
				error('ZeroDivisionError')
		elif stack[-1]:
			stack[-1] = 0
		else:
			error('ZeroDivisionError')
	elif n == ';': # 59
		stack.pop()
		if not len(stack):
			numpad('clear')
	elif n == '@': # 64
		stack.append(stack.pop(0))
	elif n == '\\': # 92
		if 1 < len(stack):
			stack.append(stack.pop(-2))
	elif n == '^': # 94
		if 1 < len(stack):
			if stack[-2:] == [0, 0]:
				error('ZeroDivisionError')
			else:
				stack.append(stack.pop(-2) ** stack.pop())
		elif stack[-1]:
			stack[-1] = 0
		else:
			error('ZeroDivisionError')
	elif n == '~': # 126
		stack[-1] *= -1
	elif n == '←': # 8592
		if isinstance(stack[-1], int):
			stack[-1] //= 10
		elif isinstance(stack[-1], float):
			stack[-1] = float(str(stack[-1])[:-1])
		else:
			error('TypeError')
	# words
	elif n == 'abs':
		stack[-1] = abs(stack[-1])
	elif n == 'acos':
		if stack[-1].imag:
			stack[-1] = cacos(stack[-1])
		else:
			stack[-1] = acos(stack[-1])
	elif n == 'and':
		if 1 < len(stack):
			if isinstance(sum(stack[-2:]), int):
				stack.append(stack.pop(-2) & stack.pop())
			else:
				error('TypeError')
		else:
			stack[-1] = 0
	elif n == 'asin':
		if stack[-1].imag:
			stack[-1] = casin(stack[-1])
		else:
			stack[-1] = asin(stack[-1])
	elif n == 'atan':
		if stack[-1].imag:
			stack[-1] = catan(stack[-1])
		else:
			stack[-1] = atan(stack[-1])
	elif n == 'cos':
		if stack[-1].imag:
			stack[-1] = ccos(stack[-1])
		else:
			stack[-1] = cos(stack[-1])
	elif n == 'exp':
		if stack[-1].imag:
			stack[-1] = cexp(stack[-1])
		elif stack[-1] < 2**9:
			stack[-1] = exp(stack[-1])
		else:
			error('OverflowError')
	elif n == 'gcd':
		if 1 < len(stack):
			if isinstance(sum(stack[-2:]), int):
				stack.append(gcd(stack.pop(), stack.pop()))
			else:
				error('DomainError')
	elif n == 'hypot':
		if 1 < len(stack):
			stack.append((stack.pop()**2 + stack.pop()**2)**.5)
	elif n == 'ln':
		if stack[-1].imag or stack[-1] < 0:
			stack[-1] = clog(stack[-1])
		elif stack[-1]:
			stack[-1] = log(stack[-1])
		else:
			error('DomainError')
	elif n == 'mod':
		if 1 < len(stack):
			if stack[-2].imag or stack[-1].imag:
				error('DomainError')
			elif stack[-1]:
				stack.append(stack.pop(-2) % stack.pop())
			else:
				error('ZeroDivisionError')
		elif stack[-1]:
			stack[-1] = 0
		else:
			error('ZeroDivisionError')
	elif n == 'not':
		if isinstance(stack[-1], int):
			stack[-1] = ~stack[-1]
		else:
			error('TypeError')
	elif n == 'or':
		if 1 < len(stack):
			if isinstance(sum(stack[-2:]), int):
				stack.append(stack.pop(-2) | stack.pop())
			else:
				error('TypeError')
	elif n == 'rand':
		stack.append(random())
	elif n == 'sin':
		if stack[-1].imag:
			stack[-1] = csin(stack[-1])
		else:
			stack[-1] = sin(stack[-1])
	elif n == 'sqrt':
		stack[-1] **= .5
	elif n == 'square':
		stack[-1] **= 2
	elif n == 'tan':
		if stack[-1].imag:
			stack[-1] = ctan(stack[-1])
		else:
			stack[-1] = tan(stack[-1])
	elif n == 'xor':
		if 1 < len(stack):
			if isinstance(sum(stack[-2:]), int):
				stack.append(stack.pop(-2) ^ stack.pop())
			else:
				error('TypeError')
	# imag check
	if isinstance(stack[-1], complex):
		if abs(stack[-1].imag) < 10**-16:
			stack[-1] = stack[-1].real
		elif abs(stack[-1].real) < 10**-16:
			stack[-1] = 1j * stack[-1].imag
	if isinstance(stack[-1], float):
		if not (stack[-1] - round(stack[-1])):
			stack[-1] = round(stack[-1])
	screen_update()
	

def screen_update():
	screen.config(text='\n'.join(str(i) for i in stack), bg='white')
	history_screen.config(text=' '.join(history), bg=defaultbg)


def system_copy(*_):
	root.clipboard_clear()
	root.clipboard_append(str(stack[-1]))
	print('Copied.')
	history_screen.config(text='Copied.', bg='#00ff00')
	root.update()
	sleep(1)
	screen_update()


def system_paste(*_):
	new = root.clipboard_get()
	for t in (int, float, complex):
		try:
			stack.append(t(new))
			screen_update()
			return t
		except ValueError:
			pass
	return None


def url_label(surface, url: str) -> tk.Label:
	import webbrowser
	url1 = tk.Label(surface, text=url, fg="blue", cursor="hand2")
	url1.pack()
	url1.bind("<Button-1>", lambda *_: webbrowser.open_new(url))
	return url1


def view_about():
	mocha_url = 'https://mocha2007.github.io/'
	repo_url = 'https://github.com/Mocha2007/mocalc'
	help_screen = tk.Tk()
	help_screen.title("About MoCalc")
	help_screen.resizable(False, False)
	tk.Label(help_screen, width=25, height=2, text='MoCalc', font=(24,)).pack()
	tk.Label(help_screen, width=25, height=2, justify='left', text='Author: Mocha2007\nLicense: GPL-3.0').pack()

	url_label(help_screen, mocha_url).pack()
	url_label(help_screen, repo_url).pack()
	tk.Label(help_screen, width=25, height=1).pack()


def view_clear():
	global idiv
	idiv = False
	for row in buttons:
		for button in row:
			if isinstance(button, tk.Button):
				button.destroy()
	try:
		history_screen.destroy()
		screen.destroy()
		gscommandlabel.destroy()
	except NameError:
		pass


def view_help(*_):
	help_screen = tk.Tk()
	help_screen.title("MoCalc Help")
	help_screen.resizable(False, False)
	help_text = open('readme.md', 'r', encoding='utf8').read()
	height = help_text.count('\n') + 1
	width = len(max(help_text.split('\n'), key=len))
	tk.Label(help_screen, width=width, height=height, justify='left', text=help_text).pack()


def view_programmer(*_):
	global idiv
	view_standard(programmer=True)
	idiv = True


def view_scientific(*_):
	global history_screen
	global screen
	global gscommandlabel
	view_clear()
	screen_width = 45

	history_screen = tk.Label(root, anchor='e', width=screen_width, height=1)
	history_screen.grid(row=0, columnspan=len(keys[-1]))
	history_screen.configure(font=("Consolas", 12))
	screen = tk.Label(root, anchor='e', width=screen_width, height=5)
	screen.grid(row=1, columnspan=len(keys[-1]))
	screen.configure(font=("Consolas", 12))
	screen.bind('<Button-1>', system_copy)
	gscommandlabel = tk.Label(root, width=5, height=1, text='Stack')
	gscommandlabel.grid(row=2, column=5)

	for i, row in enumerate(keys):
		for j, k in enumerate(row):
			if not k:
				continue
			buttons[i][j] = tk.Button(root, text=k, height=1, width=5, command=(lambda k: lambda: numpad(k))(k))
			buttons[i][j].grid(row=i+2, column=j)
			try:
				root.bind(k, (lambda k: lambda *_: numpad(k))(k))
			except TclError:
				pass
	del i, row, j, k
	tk.Button(root, text='CLEAR', height=3, width=5, command=lambda: numpad('clear')).grid(row=3, column=4, rowspan=2)
	tk.Button(root, text='ENTER', height=3, width=5, command=lambda: numpad('↵')).grid(row=5, column=4, rowspan=2)
	tk.Button(root, text='0', height=1, width=12, command=lambda: numpad('0')).grid(row=6, column=0, columnspan=2)
	screen_update()


def view_standard(*_, **kwargs):
	global history_screen
	global screen
	view_clear()
	screen_width = 25
	programmer = 'programmer' in kwargs and kwargs['programmer']

	history_screen = tk.Label(root, anchor='e', width=screen_width, height=1)
	history_screen.grid(row=0, columnspan=len(keys[-1]))
	history_screen.configure(font=("Consolas", 12))
	screen = tk.Label(root, anchor='e', width=screen_width, height=5)
	screen.grid(row=1, columnspan=len(keys[-1]))
	screen.configure(font=("Consolas", 12))
	screen.bind('<Button-1>', system_copy)

	for i, row in enumerate(programmer_keys if programmer else keys):
		for j, k in enumerate(row):
			if not k or 4 < j:
				continue
			buttons[i][j] = tk.Button(root, text=k, height=1, width=5, command=(lambda k: lambda: numpad(k))(k))
			buttons[i][j].grid(row=i+2, column=j)
			try:
				root.bind(k, (lambda k: lambda *_: numpad(k))(k))
			except TclError:
				pass
	del i, row, j, k
	tk.Button(root, text='CLEAR', height=3, width=5, command=lambda: numpad('clear')).grid(row=3, column=4, rowspan=2)
	tk.Button(root, text='ENTER', height=3, width=5, command=lambda: numpad('↵')).grid(row=5, column=4, rowspan=2)
	tk.Button(root, text='0', height=1, width=12, command=lambda: numpad('0')).grid(row=6, column=0, columnspan=2)
	screen_update()


# make the gui
root = tk.Tk()
root.title("MoCalc")
root.resizable(False, False)
defaultbg = root.cget('bg')

view_scientific()

# extra binds
for shortcut, command in shortcuts.items():
	root.bind(shortcut, (lambda k: lambda *_: numpad(k))(command))
del shortcut, command
root.bind('<Control-c>', system_copy)
root.bind('<Control-v>', system_paste)
root.bind('<F1>', view_help)
# the menu
menubar = tk.Menu(root)

menu_file = tk.Menu(root, tearoff=0)
menu_file.add_command(label="Exit", command=quit)
menubar.add_cascade(label="File", menu=menu_file)

menu_view = tk.Menu(root, tearoff=0)
menu_view.add_command(label="Standard", command=view_standard)
menu_view.add_command(label="Scientific", command=view_scientific)
menu_view.add_command(label="Programmer", command=view_programmer)
menubar.add_cascade(label="View", menu=menu_view)

menu_edit = tk.Menu(root, tearoff=0)
menu_edit.add_command(label="Copy", command=system_copy)
menu_edit.add_command(label="Paste", command=system_paste)
menubar.add_cascade(label="Edit", menu=menu_edit)

menu_help = tk.Menu(root, tearoff=0)
menu_help.add_command(label="View Help", command=view_help)
menu_help.add_command(label="About", command=view_about)
menubar.add_cascade(label="Help", menu=menu_help)

root.config(menu=menubar)
# if argv
if sys.argv[1:]:
	for arg in sys.argv[1:]:
		numpad(arg)
	print(stack[-1])
	exit()
# done!
screen_update()
root.mainloop()
