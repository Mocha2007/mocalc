from math import log
from cmath import log as clog
from time import sleep
import tkinter as tk
# ty https://www.python-course.eu/tkinter_buttons.php <3

digits = '0123456789'
keys = [
	['~', 'sqrt', 'square', '^', 'ln'],
	['7', '8', '9', '/', ''],
	['4', '5', '6', '*', '', '$'],
	['1', '2', '3', '-', '', '@'],
	['', '', '%', '+', '', '\\'],
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
	try:
		print(n)
	except UnicodeEncodeError:
		print('...')
	history.append(n)
	if n in digits: # 48-57
		n = int(n)
		stack[-1] *= 10
		stack[-1] += n if 0 <= n else -n
	# speshul
	elif n == 'clear':
		stack = [0]
		history = []
	elif n == '↵':
		stack.append(0)
	# other than special
	elif n == '$': # 64
		index = stack.pop()
		if isinstance(index, int):
			if len(stack) and abs(index) <= len(stack):
				stack.append(stack[index])
			else:
				error('IndexError')
		else:
			error('TypeError')
	elif n == '%': # 37
		stack[-1] /= 100
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
			stack.append(stack.pop(-2) / stack.pop())
		else:
			if stack[-1]:
				stack[-1] = 0
			else:
				error('ZeroDivisionError')
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
		else:
			if stack[-1]:
				stack[-1] = 0
			else:
				error('ZeroDivisionError')
	elif n == '~': # 126
		stack[-1] *= -1
	# words
	elif n == 'ln':
		if stack[-1].imag or stack[-1] < 0:
			stack[-1] = clog(stack[-1])
		elif stack[-1]:
			stack[-1] = log(stack[-1])
		else:
			error('DomainError')
	elif n == 'sqrt':
		stack[-1] **= .5
	elif n == 'square':
		stack[-1] **= 2
	screen_update()

def screen_update():
	screen.config(text='\n'.join(str(i) for i in stack), bg='white')
	history_screen.config(text=' '.join(history))

# make the gui
screen_width = 34
 
root = tk.Tk()
root.title("MoCalc")
root.resizable(False, False)
history_screen = tk.Label(root, anchor='e', width=screen_width, height=1)
history_screen.grid(row=0, columnspan=len(keys[0])+1)
history_screen.configure(font=("Consolas", 12))
screen = tk.Label(root, anchor='e', width=screen_width, height=5)
screen.grid(row=1, columnspan=len(keys[0])+1)
screen.configure(font=("Consolas", 12))
gscommandlabel = tk.Label(root, width=5, height=2, text='GS\nComms')
gscommandlabel.grid(row=2, column=5)


for i, row in enumerate(keys):
	for j, k in enumerate(row):
		if not k:
			continue
		buttons[i][j] = tk.Button(root, text=k, height=2, width=6, command=(lambda k: lambda: numpad(k))(k))
		buttons[i][j].grid(row=i+2, column=j)
		root.bind(k, (lambda k: lambda *_: numpad(k))(k))
del i, row, j, k
tk.Button(root, text='CLEAR', height=5, width=6, command=lambda: numpad('clear')).grid(row=3, column=4, rowspan=2)
tk.Button(root, text='ENTER', height=5, width=6, command=lambda: numpad('↵')).grid(row=5, column=4, rowspan=2)
tk.Button(root, text='0', height=2, width=13, command=lambda: numpad('0')).grid(row=6, column=0, columnspan=2)
# extra binds
root.bind('<Return>', lambda *_: numpad('↵'))
root.bind('<BackSpace>', lambda *_: numpad('clear'))
# done!
screen_update()
root.mainloop()
