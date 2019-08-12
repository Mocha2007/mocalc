from math import acos, asin, atan, cos, exp, factorial, gamma, gcd, log, sin, tan
from cmath import acos as cacos, asin as casin, atan as catan, cos as ccos, exp as cexp, log as clog, sin as csin, tan as ctan
from random import random
from time import sleep
import sys
import tkinter as tk
from _tkinter import TclError
# ty https://www.python-course.eu/tkinter_buttons.php <3

digits = '0123456789'
keys = [
	['~', 'sqrt', 'square', '^', '←', '', '', 'abs', 'gcd'],
	['7', '8', '9', '/', '', ';', 'not', 'rand', 'ln', 'hypot'],
	['4', '5', '6', '*', '', '$', 'and', '!', 'sin', 'asin'],
	['1', '2', '3', '-', '', '@', 'or', 'exp', 'cos', 'acos'],
	['', '', '%', '+', '', '\\', 'xor', 'mod', 'tan', 'atan'],
]
buttons = keys
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
	if n in {'acos', 'asin', 'atan'} and not (-1 <= stack[-1] <= 1):
		return error('DomainError')
	# main
	if n in digits: # 48-57
		n = int(n)
		stack[-1] *= 10
		stack[-1] += n if 0 <= n else -n
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
	elif n == '/': # 47
		if 1 < len(stack):
			if stack[-1]:
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
	screen_update()

def screen_update():
	screen.config(text='\n'.join(str(i) for i in stack), bg='white')
	history_screen.config(text=' '.join(history))

# make the gui
screen_width = 50
 
root = tk.Tk()
root.title("MoCalc")
root.resizable(False, False)
history_screen = tk.Label(root, anchor='e', width=screen_width, height=1)
history_screen.grid(row=0, columnspan=len(keys[-1]))
history_screen.configure(font=("Consolas", 12))
screen = tk.Label(root, anchor='e', width=screen_width, height=5)
screen.grid(row=1, columnspan=len(keys[-1]))
screen.configure(font=("Consolas", 12))
gscommandlabel = tk.Label(root, width=5, height=1, text='GS')
gscommandlabel.grid(row=2, column=5)
bitwisecommandlabel = tk.Label(root, width=5, height=1, text='Bit')
bitwisecommandlabel.grid(row=2, column=6)


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
# extra binds
root.bind('<Return>', lambda *_: numpad('↵'))
root.bind('<BackSpace>', lambda *_: numpad('←'))
root.bind('<Delete>', lambda *_: numpad('clear'))
# if argv
if sys.argv[1:]:
	for arg in sys.argv[1:]:
		numpad(arg)
	print(stack[-1])
	exit()
# done!
screen_update()
root.mainloop()