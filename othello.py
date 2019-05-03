##############################################
# Othello game for python
# May 3rd Reiwa 1
##############################################
# -*- coding: utf-8 -*-
import os
from enum import IntEnum
import random
import time

#リアルタイムにキーボード入力を処理する
import readchar

#キー入力処理。
import  msvcrt

#これはキーロガーとして使える。
from pyhooked import Hook, KeyboardEvent, MouseEvent

#########################################################################
# ブロック表示用各変数

BOARD_WIDTH = 8
BOARD_HEIGHT = 8

BLOCK_TYPE_MAX = 7

class COLOR(IntEnum):
	NONE = -1
	BLACK = 0
	WHITE = 1
	MAX = 2

Stone = ["〇", "●"]

class DIRECTION(IntEnum):
	UP = 0
	UP_LEFT = 1
	LEFT = 2
	DOWN_LEFT = 3
	DOWN = 4
	DOWN_RIGHT = 5
	RIGHT = 6
	UP_RIGHT = 7
	MAX = 8

directions = [[0, -1],	# UP
			 [-1, -1],	# UP_LEFT
			 [-1, 0],	# LEFT
			 [-1, 1],	# DOWN_LEFT
			 [0, 1],	# DOWN
			 [1, 1],	# DOWN_RIGHT
			 [1, 0],	# RIGHT
			 [1, -1]]	# UP_RIGHT

colorNames = ["Black","White"]
cantPut = False
cells = [[0 for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
checked = [[0 for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
#########################################################################

# 処理中止の入力用
CTRL_C = 3

# key input
try:
	from msvcrt import getch
except ImportError:
	def getch():
		import sys
		import tty
		import termios
		fd = sys.stdin.fileno()
		old = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			return sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old)

################################################
#引数で指定されたリストの要素すべてに_valを代入
################################################
def fillList(_list, _val):
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			_list[y][x] = _val

#################################################################
# 画面に表示する記号を保持する、cells[y][x]に初期値を代入。
#################################################################
def InitCells():
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			cells[y][x] = COLOR.NONE
	cells[3][3] = cells[4][4] = COLOR.WHITE
	cells[4][3] = cells[3][4] = COLOR.BLACK

################################################
# cells[y][x]にしたがって画面表示
################################################
def display(_cursorX, _cursorY, _turn):
	global locked
	global cantPut
	os.system('cls')
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			if x == _cursorX and y == _cursorY:
				print("◎", end="")
			else:
				if cells[y][x] == COLOR.NONE:
					if y % 2 == 0:print("■" if x % 2 == 0 else "　", end="")
					else:print("■" if x % 2 != 0 else "　", end="")
				elif cells[y][x] == COLOR.BLACK:print(Stone[COLOR.BLACK], end="")
				elif cells[y][x] == COLOR.WHITE:print(Stone[COLOR.WHITE], end="")
				else:print("・", end="")
		print("")
	if cantPut:
		print("Can't put!")
	else:
		print("{}'s turn.".format(colorNames[_turn]))

##########################
# 石を置けるかの判定
##########################
def checkCanPut(_color, _x, _y, _turnOver):
	if cells[_y][_x] != COLOR.NONE:
		return False

	colorOponent = COLOR.BLACK if _color == COLOR.WHITE else COLOR.WHITE
	for i in range(DIRECTION.MAX):
		x = _x
		y = _y
		x += directions[i][0]
		y += directions[i][1]
		if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
			continue
		if cells[y][x] != colorOponent:
			continue

		while(True):
			x += directions[i][0]
			y += directions[i][1]
			
			if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
				break
			if cells[y][x] == COLOR.NONE:
				break
			if cells[y][x] == _color:
				if not _turnOver:
					return True
				x2 = _x
				y2 = _y
				while(True):
					cells[y2][x2] = _color
					x2 += directions[i][0]
					y2 += directions[i][1]
					
					if x2 == x and y2 == y:
						break
	return False

##########################
# 石を置けるかの判定
##########################
def checkCanPutAll(_color):
	for y in range(BOARD_HEIGHT):
		for x in range(BOARD_WIDTH):
			if checkCanPut(_color, x, y, False):
				return True
	return False

################################################
# Othello Game main
################################################
def main():

	cursorX = 0
	cursorY = 0
	selectedX = -1
	selectedY = -1
	turn = COLOR.BLACK
	global cantPut

	InitCells()
	while(True):
		display(cursorX, cursorY, turn)
		cantPut = False
		chIn = readchar.readkey()
		if chIn == CTRL_C:
			break
		if chIn == 'k' or chIn == 'K':
			cursorY = 0 if cursorY - 1 < 0 else cursorY - 1
		elif chIn == 'j' or chIn == 'J':
			cursorY = BOARD_HEIGHT -1 if cursorY + 1 >= BOARD_HEIGHT else cursorY + 1
		elif chIn == 'h' or chIn == 'H':
			cursorX = 0 if cursorX - 1 < 0 else cursorX - 1
		elif chIn == 'l' or chIn == 'L':
			cursorX = BOARD_WIDTH -1  if cursorX + 1 >= BOARD_WIDTH else cursorX + 1
		elif chIn == 'x' or chIn == 'X':
			break
		else:
			if not checkCanPut(turn, cursorX, cursorY, False):
				cantPut = True
			else:
				checkCanPut(turn, cursorX, cursorY, True)
				cells[cursorY][cursorX] = turn
				turn = COLOR.BLACK if turn == COLOR.WHITE else COLOR.WHITE
				if not checkCanPutAll(turn):
					turn = COLOR.BLACK if turn == COLOR.WHITE else COLOR.WHITE
		# Both Black and White can not put the stone, then the game is over.
		if not checkCanPutAll(COLOR.BLACK) and not checkCanPutAll(COLOR.WHITE):
			count = [0 for n in range(COLOR.MAX)]
			for y in range(BOARD_HEIGHT):
				for x in range(BOARD_WIDTH):
					if cells[y][x] != COLOR.NONE:
						count[cells[y][x]] += 1

			display(cursorX, cursorY, turn)
			for i in range(COLOR.MAX):
				print("{}:{}".format(colorNames[i], count[i]))
			if count[COLOR.BLACK] == count[COLOR.WHITE]:
				print("Draw!")
			else:
				if count[COLOR.BLACK] > count[COLOR.WHITE]:
					print("{} ".format(colorNames[COLOR.BLACK]), end="")
				else:
					print("{} ".format(colorNames[COLOR.WHITE]), end="")
				print("Won!")
			readchar.readkey()
			break

if __name__ == '__main__':
	main()
