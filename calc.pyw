from math import factorial, gamma, gcd
from cmath import acos, asin, atan, cos, exp, log, sin, tan
from random import random
from time import sleep
from copy import deepcopy
import sys
import tkinter as tk
from _tkinter import TclError
from PIL import Image, ImageTk, __version__ as pilv
# note to self https://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm

imgsize = 400 # pixels, square
img_filename = 'graph.png'

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
for ki, krow in enumerate(keys):
	for kj, kk in enumerate(krow):
		key_coords[kk] = ki, kj
graphing_objects = []

# set up vars
stack = [0]
history = []


# functions
def blank_graph():
	Image.new('RGB', (imgsize,)*2, color='white').save(img_filename)


def derivative(fx, n: int = 1):
	"""takes and returns a function of one variable"""
	assert isinstance(n, int) and 0 < n
	tol = 1e-6
	n -= 1
	if n:
		return derivative(derivative(fx, n))
	return lambda x: (fx(x+tol) - fx(x)) / tol


def integral(fx):
	"""takes and returns a function of one variable"""
	res = 10

	def integration(x: float):
		s = 0
		for i in range(res):
			try:
				s += (fx(x-i*x/res) + fx(x-(i+1)*x/res))/2 * x/res
			except ValueError:
				pass
		return s
	return integration


def draw():
	resolution = 16 # 16 w/ x*sin(1/x) -> 30ms
	img = Image.new('RGB', (imgsize,)*2, color='white')

	pixels = img.load()
	domain_min, domain_max, range_min, range_max = limits
	pieces = resolution*img.size[0]
	domain = tuple(domain_min + (domain_max - domain_min)/pieces * i for i in range(pieces))
	for i, x in enumerate(domain): # col (x, increasing)
		i //= resolution
		try:
			y = f(x)
		except ZeroDivisionError: # draw vertical asym
			for j in range(0, img.size[1], 2):
				pixels[i, j] = 255, 0, 0
			continue
		except (OverflowError, ValueError):
			continue
		try:
			if y.imag:
				j = img.size[1] - round((y.imag - range_min) / (range_max - range_min) * img.size[1])
				if j in range(img.size[1]):
					pixels[i, j] = 255, 128, 0
			j = img.size[1] - round((y.real - range_min) / (range_max - range_min) * img.size[1])
			if j in range(img.size[1]):
				pixels[i, j] = 0, 0, 255
		except (OverflowError, ValueError):
			continue
	# save!~
	img.save(img_filename)


def error(name: str = 'Error'):
	print(name)
	screen.config(text=name, bg='red')
	root.update()
	sleep(1)
	numpad('clear')


def main(n: str):
	global history, stack

	if graphing_on:
		return screen_update()

	history.append(n)
	# main
	if n in digits: # 48-57
		stack[-1] = float(str(stack[-1]) + n)
	# speshul
	elif n == 'clear':
		stack, history = [0], []
	elif n in {'↵', '=', 'enter', 'return'}:
		stack.append(0)
	# other than special
	elif n == '!': # 33
		if isinstance(stack[-1], int):
			stack[-1] = factorial(stack[-1])
		else:
			stack[-1] = gamma(stack[-1] + 1)
	elif n == '$': # 36
		stack.append(stack[stack.pop()])
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
	elif n in {'/', 'idiv'}: # 47
		if 1 < len(stack):
			if idiv or n == 'idiv':
				stack.append(stack.pop(-2) // stack.pop())
			else:
				stack.append(stack.pop(-2) / stack.pop())
		else:
			stack[-1] = 0
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
			stack.append(stack.pop(-2) ** stack.pop())
		else:
			stack[-1] = 0
	elif n == '~': # 126
		stack[-1] *= -1
	elif n == '←': # 8592
		if isinstance(stack[-1], int):
			stack[-1] //= 10
		else:
			stack[-1] = float(str(stack[-1])[:-1])
	# words
	elif n == 'abs':
		stack[-1] = abs(stack[-1])
	elif n == 'acos':
		stack[-1] = acos(stack[-1])
	elif n == 'and':
		if 1 < len(stack):
			stack.append(stack.pop(-2) & stack.pop())
		else:
			stack[-1] = 0
	elif n == 'asin':
		stack[-1] = asin(stack[-1])
	elif n == 'atan':
		stack[-1] = atan(stack[-1])
	elif n == 'cos':
		stack[-1] = cos(stack[-1])
	elif n == 'exp':
		stack[-1] = exp(stack[-1])
	elif n == 'gcd':
		if 1 < len(stack):
			stack.append(gcd(stack.pop(), stack.pop()))
	elif n == 'hypot':
		if 1 < len(stack):
			stack.append((stack.pop()**2 + stack.pop()**2)**.5)
	elif n == 'ln':
		stack[-1] = log(stack[-1])
	elif n == 'mod':
		if 1 < len(stack):
			stack.append(stack.pop(-2) % stack.pop())
		else:
			stack[-1] = 0
	elif n == 'not':
		stack[-1] = ~stack[-1]
	elif n == 'or':
		if 1 < len(stack):
			stack.append(stack.pop(-2) | stack.pop())
	elif n == 'rand':
		stack.append(random())
	elif n == 'sin':
		stack[-1] = sin(stack[-1])
	elif n == 'sqrt':
		stack[-1] **= .5
	elif n == 'square':
		stack[-1] **= 2
	elif n == 'tan':
		stack[-1] = tan(stack[-1])
	elif n == 'xor':
		if 1 < len(stack):
			stack.append(stack.pop(-2) ^ stack.pop())
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


def numpad(n: str):
	try:
		main(n)
	except Exception as e:
		error(str(e))


def get_input(text_box: tk.Text) -> str:
	return text_box.get('1.0', 'end-1c')


def screen_update(*_):
	global f, graph_image, limits
	if graphing_on:
		history_screen.config(text='Good Input.', bg='#00ff00')
		# f
		try:
			f = eval('lambda x:'+get_input(textbox_function))
		except Exception as e:
			history_screen.config(text='Function: {}'.format(e), bg='red')
			return root.update()
		# lims
		limits = [-1, 1, -1, 1] # xmin, xmax, ymin, ymax
		boxes = textbox_domain_min, textbox_domain_max, textbox_range_min, textbox_range_max
		for i, limit in enumerate(limits):
			try:
				limits[i] = float(get_input(boxes[i]))
			except Exception as e:
				history_screen.config(text='Limit {}: {}'.format(i, e), bg='red')
				return root.update()
		# draw
		try:
			draw()
		except Exception as e:
			history_screen.config(text='Function: {}'.format(e), bg='red')
			return root.update()
		graph_image = ImageTk.PhotoImage(Image.open(img_filename))
		screen.config(image=graph_image)
		return root.update()
	screen.config(text='\n'.join(str(i) for i in stack), bg='white')
	history_screen.config(text=' '.join(history), bg=defaultbg)


def system_copy(*_):
	root.clipboard_clear()
	addendum = history_screen.cget('text') if graphing_on else str(stack[-1])
	root.clipboard_append(addendum)
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
	from webbrowser import open_new
	url1 = tk.Label(surface, text=url, fg="blue", cursor="hand2")
	url1.pack()
	url1.bind("<Button-1>", lambda *_: open_new(url))
	return url1


def view_about():
	mocha_url = 'https://mocha2007.github.io/'
	repo_url = 'https://github.com/Mocha2007/mocalc'
	help_screen = tk.Tk()
	help_screen.title("About MoCalc")
	help_screen.resizable(False, False)
	tk.Label(help_screen, width=25, height=2, text='MoCalc', font=(24,)).pack()
	tk.Label(help_screen, width=25, height=2, justify='left', text='Author: Mocha2007\nLicense: GPL-3.0').pack()
	versioninfo = 'Using:\nPython {}\nPIL {}'.format(sys.version[:5], pilv)
	tk.Label(help_screen, width=25, height=3, justify='left', text=versioninfo).pack()

	url_label(help_screen, mocha_url).pack()
	url_label(help_screen, repo_url).pack()
	tk.Label(help_screen, width=25, height=1).pack()


def view_cez(toggle: bool = True):
	global clear_button, enter_button, zero_button
	if toggle:
		if 'clear_button' not in globals():
			clear_button = tk.Button(root, text='CLEAR', height=3, width=5, command=lambda: numpad('clear'))
			clear_button.grid(row=3, column=4, rowspan=2)
			enter_button = tk.Button(root, text='ENTER', height=3, width=5, command=lambda: numpad('↵'))
			enter_button.grid(row=5, column=4, rowspan=2)
			zero_button = tk.Button(root, text='0', height=1, width=12, command=lambda: numpad('0'))
			zero_button.grid(row=6, column=0, columnspan=2)
		return None
	try:
		clear_button.destroy()
		enter_button.destroy()
		zero_button.destroy()
		del clear_button, enter_button, zero_button
	except NameError:
		pass


def view_clear():
	global graphing_objects, graphing_on, idiv
	graphing_on, idiv = [False]*2
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
	# graph shit
	for shit in graphing_objects:
		shit.destroy()
	graphing_objects = []


def view_graphing(*_):
	# https://stackoverflow.com/a/35024600/2579798
	global graphing_objects, graphing_on, screen, history_screen, graph_image, gscommandlabel
	global textbox_function, textbox_domain_min, textbox_domain_max, textbox_range_min, textbox_range_max
	view_clear()
	view_cez(False)
	graphing_on = True
	text_width = 12
	# status bar
	history_screen = tk.Label(root, anchor='e', width=3*text_width+8, height=1)
	history_screen.grid(row=0, columnspan=3)
	history_screen.configure(font=("Consolas", 12))
	history_screen.bind('<Button-1>', system_copy)
	# graph screen
	graph_image = tk.PhotoImage(file=img_filename, master=root)
	screen = tk.Label(root, image=graph_image, width=imgsize, height=imgsize)
	screen.grid(row=1, columnspan=3)
	# labels
	gscommandlabel = tk.Label(root, anchor='e', justify='right', width=text_width, height=3, text='f(x)\nDomain\nRange')
	gscommandlabel.grid(row=2, column=0, rowspan=3)
	# text boxes
	textbox_function = tk.Text(root, height=1, width=3*text_width)
	textbox_function.grid(row=2, column=1, columnspan=2)
	textbox_function.insert(tk.END, 'x')

	textbox_domain_min = tk.Text(root, height=1, width=text_width)
	textbox_domain_min.grid(row=3, column=1)
	textbox_domain_min.insert(tk.END, '-1')

	textbox_domain_max = tk.Text(root, height=1, width=text_width)
	textbox_domain_max.grid(row=3, column=2)
	textbox_domain_max.insert(tk.END, '1')

	textbox_range_min = tk.Text(root, height=1, width=text_width)
	textbox_range_min.grid(row=4, column=1)
	textbox_range_min.insert(tk.END, '-1')

	textbox_range_max = tk.Text(root, height=1, width=text_width)
	textbox_range_max.grid(row=4, column=2)
	textbox_range_max.insert(tk.END, '1')
	# finish
	graphing_objects = [textbox_function, textbox_domain_min, textbox_domain_max, textbox_range_min, textbox_range_max]
	screen_update()


def view_help(*_):
	help_screen = tk.Tk()
	help_screen.title("MoCalc Help")
	help_screen.resizable(False, False)
	help_text = open('readme.md', 'r', encoding='utf8').read()
	height = help_text.count('\n') + 1
	width = len(max(help_text.split('\n'), key=len))
	tk.Label(help_screen, width=width, height=height, justify='left', text=help_text).pack()


def view_programmer(*_):
	view_scientific(mode='programmer')


def view_scientific(*_, **kwargs):
	global history_screen, screen, gscommandlabel, idiv, stack
	view_clear()
	# establish mode
	mode = kwargs['mode'] if 'mode' in kwargs else 'scientific'
	# continue
	screen_width = 45 if mode == 'scientific' else 25

	history_screen = tk.Label(root, anchor='e', width=screen_width, height=1)
	history_screen.grid(row=0, columnspan=len(keys[-1]))
	history_screen.configure(font=("Consolas", 12))
	screen = tk.Label(root, anchor='e', width=screen_width, height=5)
	screen.grid(row=1, columnspan=len(keys[-1]))
	screen.configure(font=("Consolas", 12))
	screen.bind('<Button-1>', system_copy)
	if mode == 'scientific':
		gscommandlabel = tk.Label(root, width=5, height=1, text='Stack')
		gscommandlabel.grid(row=2, column=5, rowspan=1)

	for i, row in enumerate(programmer_keys if mode == 'programmer' else keys):
		for j, k in enumerate(row):
			if not k:
				continue
			if mode != 'scientific' and 4 < j:
				continue
			buttons[i][j] = tk.Button(root, text=k, height=1, width=5, command=(lambda x: lambda: numpad(x))(k))
			buttons[i][j].grid(row=i+2, column=j)
			try:
				root.bind(k, (lambda x: lambda *_: numpad(x))(k))
			except TclError:
				pass
	view_cez()
	screen_update()
	if mode == 'programmer':
		idiv = True
		numpad('clear')


def view_standard(*_):
	view_scientific(mode='standard')


# if argv
if sys.argv[1:]:
	if sys.argv[1] == 'graph':
		limits = map(float, sys.argv[2:6])
		f = eval('lambda x:'+' '.join(sys.argv[6:]))
		draw()
	else:
		for arg in sys.argv[1:]:
			numpad(arg)
		print(stack[-1])
	exit()

# make the gui
root = tk.Tk()
root.title("MoCalc")
root.resizable(False, False)
defaultbg = root.cget('bg')
blank_graph()

# view_scientific()
view_scientific()

# extra binds
for shortcut, command in shortcuts.items():
	root.bind(shortcut, (lambda k: lambda *_: numpad(k))(command))
root.bind('<Control-c>', system_copy)
root.bind('<Control-v>', system_paste)
root.bind('<F1>', view_help)
root.bind('<Key>', screen_update)
# the menu
menubar = tk.Menu(root)

menu_file = tk.Menu(root, tearoff=0)
menu_file.add_command(label="Exit", command=quit)
menubar.add_cascade(label="File", menu=menu_file)

menu_view = tk.Menu(root, tearoff=0)
menu_view.add_command(label="Standard", command=view_standard)
menu_view.add_command(label="Scientific", command=view_scientific)
menu_view.add_command(label="Programmer", command=view_programmer)
menu_view.add_command(label="Graphing", command=view_graphing)
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
# done!
screen_update()
root.mainloop()
