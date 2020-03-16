import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 700

GEN = 0
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


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
		self.img =self.IMGS[0]

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


class Pipe:
	GAP = 200
	VEL = 5

	def __init__(self, x):
		self.x = x
		self.height = 0
		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)   # pipe that is needed upside down
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50,450)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):

		''' mask stores the actual pixels presents in form of 2Dlist, 
		this will help us identify weather the objects actually collide or not'''
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
		# offset will tell us how far the objects are
		#top offset is dist between bird and top pipe
		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
		# Find point of collision
		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)
		#overlap returns None if no overlap

		if b_point or t_point:
			return True

		return False


class Base:
	VEL = 5
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -=self.VEL
		self.x2 -=self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH <0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1,self.y))
		win.blit(self.IMG, (self.x2,self.y))

def draw_window(win, birds, pipes, base, score, gen):
	win.blit(BG_IMG,(0,0))  #blit draws the image at specified coordinate on the window

	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

	text = STAT_FONT.render("Gen: " + str(gen),1,(255,255,255))
	win.blit(text, (10, 10))

	base.draw(win)
	for bird in birds:
		bird.draw(win)
	pygame.display.update()



def main(genomes, config):
	global GEN
	GEN +=1
	nets = []
	ge = []
	birds = []

	for _,g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230,320))
		g.fitness = 0
		ge.append(g)


	base = Base(620)
	pipes = [Pipe(640)]

	win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	clock = pygame.time.Clock()
	run = True
	score = 0

	while run:
		clock.tick(30)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
		#bird.move()

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1
		else:
			run = False
			break


		for x,bird in enumerate(birds):
			bird.move()
			ge[x].fitness +=0.1

			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

			if output[0] >0.4:
				bird.jump()

		rem = []
		add_pipe =False
		for pipe in pipes:
			for x,bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -=1
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)


				if not pipe.passed and pipe.x < bird.x :
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)


			pipe.move()
		if add_pipe:
			score+=1
			for g in ge:
				g.fitness += 3
			pipes.append(Pipe(600))

		for r in rem:
			pipes.remove(r)

		for x,bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 620 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)
				



		base.move()
		draw_window(win, birds, pipes, base, score, GEN)		


def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
		neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	p.add_reporter(neat.StatisticsReporter())
	winner = p.run(main,50)




if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)