import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500
WIN_HEIGHT = 800


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION =25 #degree of rotation
	ROT_VELOCITY = 20 #speed of rotation
	ANIMATION_SPEED = 5 # in ms, time for which one image will be shown


	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.image =self.IMGS[0]

	def jump(self):
		self.vel =-10.5  # moving up we will need negative velocity as top left corner is at (0,0)
		self.tick_count = 0 #keeps track of last time we jumped
		self.height =self.y  # keeps track of height from which we jumped


	def move(self):
		'''this function will be called 30 times per second giving the game 30 fps'''
		self.tick_count += 1 #bird moved hence a tick happened
		displacement = self.vel*self.tick_count  +  1.5*self.tick_count**2  #physics law s = vt +0.5*a*t**2

		if displacement >=16:
			displacement = 16  # setting the terminal velocity

		if displacement <=0:
			displacement =-2  #setting jump velocity

		self.y +=displacement


		if displacement < 0 or self.y < self.height + 50 :   #if bird is moving up or just began to drop then tilt the bird and not tilt the bird completely backward
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION

		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VELOCITY  #if bird is moving down the let it nose dive


	def draw(self,win):
		self.img_count +=1

		''' What the next if statements will do is essentially tell us which image to show
		starting with 0 as wings UP 1 as wings Parallel 2 as wings DOWN
		and back as paallel and up indicating on flap of the bird'''

		if self.img_count < self.ANIMATION_SPEED:
			self.img = self.IMGS[0]

		elif self.img_count < self.ANIMATION_SPEED*2:
			self.img = self.IMGS[1]

		elif self.img_count < self.ANIMATION_SPEED*3:
			self.img = self.IMGS[2]


		elif self.img_count < self.ANIMATION_SPEED*4:
			self.img = self.IMGS[1]


		elif self.img_count == self.ANIMATION_SPEED*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0 

		'''What the next if statement will do is not let the bird flap its wings while it is nose diving downwards'''

		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_SPEED*2


		rotated_img = pygame.transform.rotate(self.img , self.tilt)  # rotate the image about top left corner but we need the image to be rotated about center

		new_rect = rotated_img.get_rect(center = self.img.get_rect(topleft = (self.x , self.y)).center)  #this will rotate the image about center

		win.blit(rotated_img, new_rect.topleft)


	def get_mask(self):
		return pygame.mask.from_surface(self.img)


def draw_window(win, bird):
	win.blit(BG_IMG,(0,0))  #blit draws the image at specified coordinate on the window
	bird.draw(win)
	pygame.display.update()



def main():
	bird = Bird(200, 200)
	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	clock = pygame.time.Clock()
	run = True

	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		bird.move()
		draw_window(win,bird)		
	pygame.quit()
	quit()

main()
