__author__ = 'Geyi Zhang'
import pygame
import sys
from pygame.constants import K_LEFT, K_RIGHT, K_SPACE, K_UP, K_DOWN, QUIT, KEYDOWN
from board import Board
#from ..base import base
#from ple.games import base
from ple.games.base.pygamewrapper import PyGameWrapper
import numpy as np
import os
import datetime
import time



class newgame(PyGameWrapper):

	def __init__(self):
		"""
		Parameters
		----------
		None

		"""
		self.height = 345 #modify height accordingly based on how long the game level is
		self.width = 345
		self.status = 2   # (2 : still alive, 1 : win, 0: dead/lose)
		actions = {
			"left": K_LEFT,
			"right": K_RIGHT,
			"jump": K_UP,
			"up": K_UP,
			"down": K_DOWN,
			"undo": K_SPACE
		}
		
		PyGameWrapper.__init__(
			self, self.width, self.height, actions=actions)

		self.rewards = {
			"positive": 0,
			"win": 1,
			"negative": 0,
			"tick": 0
		}
		self.allowed_fps = 30
		self._dir = os.path.dirname(os.path.abspath(__file__))
		print(self._dir)
		self.datafile = open(self._dir+"\datafile.txt","a") 
		self.datafile.write(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))+"- "*30+'\n')

		self.IMAGES = {
			"right": pygame.image.load(os.path.join(self._dir, 'assets/right1.png')),
			"right2": pygame.image.load(os.path.join(self._dir, 'assets/right1.png')),
			"left": pygame.image.load(os.path.join(self._dir, 'assets/left1.png')),
			"left2": pygame.image.load(os.path.join(self._dir, 'assets/left1.png')),
			"still": pygame.image.load(os.path.join(self._dir, 'assets/still.png'))
		}

		self.prev_position = []

	def init(self):

		# Create a new instance of the Board class
		self.newGame = Board(
			self.width,
			self.height,
			self.rewards,
			self.rng,
			self._dir)

		# Assign groups from the Board instance that was created
		self.playerGroup = self.newGame.playerGroup
		self.wallGroup = self.newGame.wallGroup
		self.ladderGroup = self.newGame.ladderGroup
		self.numactions = 0
	def getScore(self):
		return self.newGame.score

	def game_over(self):
		if(self.numactions > 2000 or self.newGame.lives <=0): #max episode length is 2000 steps.
			self.numactions = 0
			return 1
		else:
			return 0

	def step(self, dt):
		self.numactions = self.numactions+1 #check number of actions taken by agent so far
		self.newGame.score += self.rewards["tick"]
		# This is where the actual game is run
		# Get the appropriate groups
		self.enemyGroup = self.newGame.enemyGroup
		self.enemyGroup2 = self.newGame.enemyGroup2
		# To check collisions below, we move the player downwards then check
		# and move him back to his original location
		self.newGame.Players[0].updateY(2)
		self.laddersCollidedBelow = self.newGame.Players[
			0].checkCollision(self.ladderGroup)
		self.wallsCollidedBelow = self.newGame.Players[
			0].checkCollision(self.wallGroup)
		self.newGame.Players[0].updateY(-2)

		# To check for collisions above, we move the player up then check and
		# then move him back down
		self.newGame.Players[0].updateY(-2)
		self.wallsCollidedAbove = self.newGame.Players[
			0].checkCollision(self.wallGroup)
		self.newGame.Players[0].updateY(2)

		# Sets the onLadder state of the player
		self.newGame.ladderCheck(
			self.laddersCollidedBelow,
			self.wallsCollidedBelow,
			self.wallsCollidedAbove)
		
		pos_x, pos_y = self.newGame.Players[0].getPosition()[0],self.newGame.Players[0].getPosition()[1]
		pos_x, pos_y = format(pos_x,'.2f'),format(pos_y,'.2f')
		position = str(pos_x) + ',' + str(pos_y)
		for event in pygame.event.get():
			# Exit to desktop
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			
			if event.type == KEYDOWN:
				# pos_x, pos_y = self.newGame.Players[0].getPosition()[0],self.newGame.Players[0].getPosition()[1]
				# pos_x, pos_y = format(pos_x,'.2f'),format(pos_y,'.2f')
				# position = str(pos_x) + ',' + str(pos_y)
				if event.key != self.actions['undo'] and self.wallsCollidedBelow:
					self.prev_position.append(self.newGame.Players[0].getPosition())
					if len(self.prev_position) >= 3:
						self.prev_position.pop(0)
						
				# Get the ladders collided with the player
				self.laddersCollidedExact = self.newGame.Players[
					0].checkCollision(self.ladderGroup)
				if (event.key == self.actions["jump"] and self.newGame.Players[0].onLadder == 0) or (
						event.key == self.actions["up"] and self.laddersCollidedExact):
					# Set the player to move up
					self.direction = 2
					if self.newGame.Players[
							0].isJumping == 0 and self.wallsCollidedBelow:
						# We can make the player jump and set his
						# currentJumpSpeed
						self.newGame.Players[0].isJumping = 1
						self.newGame.Players[0].currentJumpSpeed = 7

				if event.key == self.actions["right"]:
					self.datafile.write(str(self.numactions)+' '+position+' right\n')
					if self.newGame.direction != 4:
						self.newGame.direction = 4
						self.newGame.cycles = -1  # Reset cycles
					self.newGame.cycles = (self.newGame.cycles + 1) % 4
					if self.newGame.cycles < 2:
						# Display the first image for half the cycles
						self.newGame.Players[0].updateWH(self.IMAGES["right"], "H",
														 self.newGame.Players[0].getSpeed(), 15, 15)
					else:
						# Display the second image for half the cycles
						self.newGame.Players[0].updateWH(self.IMAGES["right2"], "H",
														 self.newGame.Players[0].getSpeed(), 15, 15)
					wallsCollidedExact = self.newGame.Players[
						0].checkCollision(self.wallGroup)
					if wallsCollidedExact:
						# If we have collided a wall, move the player back to
						# where he was in the last state
						self.newGame.Players[0].updateWH(self.IMAGES["right"], "H",
														 -self.newGame.Players[0].getSpeed(), 15, 15)

				if event.key == self.actions["left"]:
					self.datafile.write(str(self.numactions)+' '+position+' left\n')
					if self.newGame.direction != 3:
						self.newGame.direction = 3
						self.newGame.cycles = -1  # Reset cycles
					self.newGame.cycles = (self.newGame.cycles + 1) % 4
					if self.newGame.cycles < 2:
						# Display the first image for half the cycles
						self.newGame.Players[0].updateWH(self.IMAGES["left"], "H",
														 -self.newGame.Players[0].getSpeed(), 15, 15)
					else:
						# Display the second image for half the cycles
						self.newGame.Players[0].updateWH(self.IMAGES["left2"], "H",
														 -self.newGame.Players[0].getSpeed(), 15, 15)
					wallsCollidedExact = self.newGame.Players[
						0].checkCollision(self.wallGroup)
					if wallsCollidedExact:
						# If we have collided a wall, move the player back to
						# where he was in the last state
						self.newGame.Players[0].updateWH(self.IMAGES["left"], "H",
														 self.newGame.Players[0].getSpeed(), 15, 15)

				# If we are on a ladder, then we can move up
				if event.key == self.actions[
                        "up"] and self.newGame.Players[0].onLadder:
					self.datafile.write(str(self.numactions)+' '+position+' up\n')
					self.newGame.Players[0].updateWH(self.IMAGES["still"], "V",
													 -self.newGame.Players[0].getSpeed() / 2, 15, 15)
					if len(self.newGame.Players[0].checkCollision(self.ladderGroup)) == 0 or len(
							self.newGame.Players[0].checkCollision(self.wallGroup)) != 0:
						self.newGame.Players[0].updateWH(self.IMAGES["still"], "V",
														 self.newGame.Players[0].getSpeed() / 2, 15, 15)
				
				# If we are on a ladder, then we can move down
				if event.key == self.actions[
                        "down"] and self.newGame.Players[0].onLadder:
					self.datafile.write(str(self.numactions)+' '+position+' down\n')
					self.newGame.Players[0].updateWH(self.IMAGES["still"], "V",
													 self.newGame.Players[0].getSpeed() / 2, 15, 15)
				
				if (event.key == self.actions['undo']):
					self.datafile.write(str(self.numactions)+' '+position+' undo\n')
					print(self.prev_position)
					if len(self.prev_position) != 0 :
						self.newGame.Players[0].setPosition(self.prev_position[-1])
						self.prev_position.pop()
		


		# Update the player's position and process his jump if he is jumping
		self.newGame.Players[0].continuousUpdate(
			self.wallGroup, self.ladderGroup)

		# Redraws all our instances onto the screen
		self.newGame.redrawScreen(self.screen, self.width, self.height)

		#enemy encounter
		enemysCollected = pygame.sprite.spritecollide(
			self.newGame.Players[0], self.enemyGroup, True)
		enemysCollected2 = pygame.sprite.spritecollide(
			self.newGame.Players[0], self.enemyGroup2, True)
		self.newGame.enemyCheck2(enemysCollected2)
		self.newGame.enemyCheck(enemysCollected)
		if self.newGame.lives == 0:
			self.datafile.write(str(self.numactions)+' '+position+' death\n')
			self.newGame.lives = 1 
		# Check if you have reached the princess
		self.status = self.newGame.checkVictory(self.status)
		if self.status == 1:
			self.datafile.write(str(self.numactions)+' '+position+' win\n')
		

if __name__ == "__main__":
	pygame.init()
	# Instantiate the Game class and run the game
	game = newgame()
	game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
	game.clock = pygame.time.Clock()
	game.rng = np.random.RandomState(24)
	game.init()

	while (game.status != 1):
		dt = game.clock.tick_busy_loop(25)
		game.step(dt)
		# print(game.game_over())
		pygame.display.update()