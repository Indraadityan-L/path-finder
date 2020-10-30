import pygame
import math
from queue import PriorityQueue
from pygame import mixer

RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
TEAL = (64, 220, 208)

pygame.init()

#this program will use a square sized window for the display with a width of 500 pixels
WIDTH = 500
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Visual of Path Finding Algorithm (Astar Implementation)");
mixer.music.load('background.wav')
pygame.mixer.music.set_volume(0.2)
mixer.music.play(-1)

class Node:
	#all the below definitions allows us to check and modify the state of each square in the whole window
	def __init__(self, row, col, width, tot_rows):
		self.row = row
		self.col  = col
		self.x = row * width
		self.y = col *width
		self.color = WHITE
		self.surrounding_squares = []
		self.width =width
		self.tot_rows = tot_rows

	#function returns the current position of the node
	def get_pos(self):
		return self.row, self.col

	#function checks if the square on the grid has been checked or not when calculating the shortest path
	def is_checked(self):
		return self.color == RED
	#check with openset
	def is_open(self):
		return self.color == GREEN

	def is_obstacle(self):
		return self.color == BLACK

	def is_end(self):
		return self.color == TEAL

	def is_start(self):
		return self.color == ORANGE

	def reset(self):
		 self.color = WHITE

	def mark_invalid(self):
		self.color = RED

	def mark_valid(self):
		self.color = GREEN

	def make_obstacle(self):
		self.color = BLACK

	def make_end(self):
		self.color = TEAL

	def mark_start(self):
		self.color = ORANGE

	def mark_path(self):
		self.color = BLUE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_surrounding_squares(self, grid):
		self.surrounding_squares = []
		if self.row < self.tot_rows -1 and not grid[self.row +1][self.col].is_obstacle():
			self.surrounding_squares.append(grid[self.row +1][self.col])

		if self.row > 0  and not grid[self.row -1][self.col].is_obstacle():
			self.surrounding_squares.append(grid[self.row -1][self.col])

		if self.col < self.tot_rows -1 and not grid[self.row][self.col+1].is_obstacle():
			self.surrounding_squares.append(grid[self.row][self.col+1])

		if self.col >0  and not grid[self.row][self.col-1].is_obstacle():
			self.surrounding_squares.append(grid[self.row][self.col -1])


	def __lt__(self, other):
		return False

def draw_path(prev_nodes, current, draw):
	length = 0
	while current in prev_nodes:
		current = prev_nodes[current]
		current.mark_path()
		length = length+1
		draw()
	return length

def estimated_dist(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return (abs(x1 - x2) + abs(y1 - y2))


def path_finder(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	prev_nodes = {} #dictionary
	curr_distance = {node: float("inf") for row in grid for node in row}
	curr_distance[start] = 0
	total_distance = {node: float("inf") for row in grid for node in row}
	total_distance[start] = estimated_dist(start.get_pos(), end.get_pos())

	open_set_hash = {start} #checks if something is in the prioirqueueu

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2] #open set will score fscore, count nand node and we want just the node hence the 2
		open_set_hash.remove(current)

		if current == end:
			#we have found the path
			length = draw_path(prev_nodes, end, draw)

			success_sound = mixer.Sound("success.wav")
			success_sound.play()
			return length
		for surrounding_sqr in current.surrounding_squares:
			temp_curr_distance = curr_distance[current] + 1

			if temp_curr_distance < curr_distance[surrounding_sqr]:
				prev_nodes[surrounding_sqr] = current
				curr_distance[surrounding_sqr] = temp_curr_distance
				total_distance[surrounding_sqr] = temp_curr_distance + estimated_dist(surrounding_sqr.get_pos(), end.get_pos())
				if surrounding_sqr not in open_set_hash:
					count = count + 1
					open_set.put((total_distance[surrounding_sqr], count, surrounding_sqr))
					open_set_hash.add(surrounding_sqr)
					surrounding_sqr.mark_valid()

		draw()

		if current != start:
			current.mark_invalid()

	return False

def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			node = Node(i, j, gap, rows)
			grid[i].append(node)

	return grid

def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
	win.fill(WHITE)
	for row in grid:
		for node in row:
			node.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows,width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col

def main(win, width):
	pygame.init()
	ROWS = 50
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True
	started = False
	while run:
		draw (win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if started:
				continue
			if pygame.mouse.get_pressed()[0]: #0 is left mouse
				pos = pygame.mouse.get_pos()
				row,col = get_clicked_pos(pos, ROWS, width)
				node = grid[row][col]
				if not start and node != end:
					start = node
					start.mark_start()
					selection_sound = mixer.Sound('select.wav')
					selection_sound.play()
				elif not end and node != start:
					end = node
					end.make_end()
					selection_sound.play()
				elif node != end and node != start:
					node.make_obstacle()

			elif pygame.mouse.get_pressed()[2]: #2 is right mouse
				pos = pygame.mouse.get_pos()
				row,col = get_clicked_pos(pos, ROWS, width)
				node = grid[row][col]
				#above three lines copied from previous stataments for doing right click
				node.reset()
				if node == start:
					start = end
				if node == end:
					end = None

			elif pygame.mouse.get_pressed()[1]:
				main(screen, WIDTH) #to restart the game

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN and not started:
					length = 0
					for row in grid:
						for node in row:
							node.update_surrounding_squares(grid)
					length = path_finder(lambda: draw(win, grid, ROWS, width), grid, start, end)
					run = False
					font = pygame.font.Font('freesansbold.ttf', 24)
					textX = 10
					textY = 10
					score = font.render("Length of path: "+str(length), True, BLACK)
					screen.blit(score, (textX,textY))
					pygame.display.update()
	run2 = True
	while run2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run2 = False
			elif pygame.mouse.get_pressed()[1]:
				main(screen, WIDTH)

	pygame.quit()
main(screen, WIDTH)
