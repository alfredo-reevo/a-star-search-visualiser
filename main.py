# // A* Search Visualizer  // #


import pygame
import math
from queue import PriorityQueue

# -- Initialisation of pygame window -- #
winWidth = 800
win = pygame.display.set_mode((winWidth, winWidth))
pygame.display.set_caption("Pathfinder Visualiser - Programmed by Alfie Reeves")

# - Colour Presets - #
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
CYAN = (0, 255, 255)
END_ORANGE = (255, 162, 0)
PATH_COLOUR = (153, 0, 255)

# -- Node Object -- #
class Node:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.colour = WHITE
        self.adjacent = []
        self.width = width
        self.totalRows = totalRows
    
    def currPos(self):
        return self.row, self.col

    def closed(self):
        return self.colour == RED

    def open(self):
        return self.colour == GREEN
    
    def obstacle(self):
        return self.colour == BLACK
    
    def start(self):
        return self.colour == CYAN

    def end(self):
        return self.colour == END_ORANGE
    
    def reset(self):
        return self.colour == WHITE

    def make_start(self):
        self.colour = CYAN
    
    def make_open(self):
        self.colour = GREEN
    
    def make_closed(self):
        self.colour = RED

    def make_obstacle(self):
        self.colour = BLACK

    def make_end(self):
        self.colour = END_ORANGE

    def make_path(self):
        self.colour = PATH_COLOUR

    def force_reset(self):
        self.colour = WHITE

    def render(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def updateAdjacent(self, grid):
        self.adjacent = []
        # Check Downwards
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].obstacle():
            self.adjacent.append(grid[self.row + 1][self.col])
        # Check Upwards
        if self.row > 0 and not grid[self.row - 1][self.col].obstacle():
            self.adjacent.append(grid[self.row - 1][self.col])
        # Check right
        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].obstacle():
            self.adjacent.append(grid[self.row][self.col + 1])
        # Check left   
        if self.col > 0 and not grid[self.row][self.col - 1].obstacle():
            self.adjacent.append(grid[self.row][self.col - 1])


    def __lt__(self,other):
        return False

# ---------------------------------------------------------------------- #

## -- A* Search Algorithm -- ##

# Using pythagoras to find the distance between node n and the end node.
def h(n1, n2):
    dist = 0

    x_1, y_1 = n1
    x_2, y_2 = n2
    dist = math.sqrt(abs((x_2 - x_1)**2) + abs((y_2 - y_1)**2))

    return dist

def reconstruct_path(came_from, current, render):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        render()


def algorithm(render, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    g_n = {node: float("inf") for row in grid for node in row}
    g_n[start] = 0

    f_n = {node: float("inf") for row in grid for node in row}
    f_n[start] = h(start.currPos(), end.currPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:        
            reconstruct_path(came_from, end, render)
            end.make_end()
            
            return True

        for adjacent in current.adjacent:
            temp_g_n = g_n[current] + 1

            if temp_g_n < g_n[adjacent]:
                came_from[adjacent] = current
                g_n[adjacent] = temp_g_n
                f_n[adjacent] = temp_g_n + h(adjacent.currPos(), end.currPos())
                if adjacent not in open_set_hash:
                    count += 1
                    open_set.put((f_n[adjacent], count, adjacent))
                    open_set_hash.add(adjacent)
                    adjacent.make_open()
        
        render()
        if current != start:
            current.make_closed()

    return False

# ---------------------------------------------------------------------- #

def gridMatrix(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def renderGrid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

def render(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.render(win)
    renderGrid(win, rows, width)
    pygame.display.update()

def clickedPos(pos, rows, width):
    gap = width // rows

    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

def main(win, width):

    endPos = []
    startPos = []

    ROWS = 50
    grid = gridMatrix(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        render(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = clickedPos(pos, ROWS, width)
                node = grid[row][col]


                if pygame.key.get_pressed()[pygame.K_LSHIFT]:     
                    startPos.clear()
                    startPos.append(node)
                    if start == None:
                        start = node
                        start.make_start()

                    elif start != node:
                        start.force_reset()
                        start = node
                        start.make_start()

                elif pygame.key.get_pressed()[pygame.K_LCTRL]:                         
                    endPos.clear()                    
                    endPos.append(node)
                    if end == None:
                        end = node
                        end.make_end()

                    elif end != node:      
                        end.force_reset()
                        end = node
                        end.make_end()

                else:
                    node.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = clickedPos(pos, ROWS, width)
                node = grid[row][col]
                node.force_reset()

                if node == start:
                    start = None
                elif node == end:
                    end == None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.updateAdjacent(grid)
                    
                    algorithm(lambda: render(win, grid, ROWS, width), grid, start, end)

    
    pygame.quit()

main(win, winWidth)