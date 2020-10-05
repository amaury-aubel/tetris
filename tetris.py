# import the pygame module, so you can use it
import pygame
import random
from shapes import buildShapes,colors

# display is divided into a square matrix of blocks
size = 20 # block size
mult = 18 # number of blocks in each direction

# speed in milliseconds of one iteration
iteration_speed = 10
# following speeds are multiplier on the speed for one iteration
# so the fastest speed attainable is max_speed * iteration_speed in ms
min_speed = 20
max_speed = 10


def displayMatrix(screen,matrix):
    """ display onto screen the matrix of blocks"""
    for i in range(mult):
        for j in range(mult):
            value = matrix[i][j]
            if value == 0: continue
            block = pygame.Rect(size*i, size*j, size-1, size-1)
            pygame.draw.rect(screen, colors[value-1], block)

def rotateShape(shape, orient):
    """ Rotate base shape based on orient
        where orient = [0..3], each value being a multiplier of 90 degrees
    """
    # only four possible states for orient
    if orient < 0: orient += 4
    orient = orient%4

    # all shapes are 4x4 matrices of blocks
    rotatedShape = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(4):
        for j in range(4):
            if orient == 0: rotatedShape[i][j] = shape[i][j]
            elif orient == 1: rotatedShape[j][3-i] = shape[i][j]
            elif orient == 2: rotatedShape[3-i][3-j] = shape[i][j]
            elif orient == 3: rotatedShape[3-j][i] = shape[i][j]
    return rotatedShape


def rotate(matrix, shape, pos, orient, angle):
    """ Rotate piece described by (shape,pos,orient) by angle
        Return True if the rotation was completed
        Return False if the rotation was not allowed        
    """
    return move(matrix,rotateShape(shape,orient+angle),pos)


def clamp(pos):
    """ Clamp position based on the dimensions of the game
        Return whether position was clamped
    """    
    if pos[0]<0: 
            pos[0]=0
            return True
    elif pos[1]<0: 
            pos[1]=0
            return True
    elif pos[0]>=mult: 
            pos[0]=mult-1
            return True
    elif pos[1]>=mult: 
            pos[1]=mult-1
            return True
    return False

def move(matrix, shape, pos, direction=(0,0)):
    """ Move the piece described by (shape,pos) in the specified direction
        Return True if the move was completed
        Return False if the move is not allowed
        
        Can be used to check that the current location of the piece is vali
        by specifying a zero direction of motion
        """
    # check first that the move is possible
    for i in range(4):
        for j in range(4):
            if shape[i][j] == 0: continue
            x = pos[0] + direction[0] + i
            y = pos[1] + direction[1] + j
            # move is impossible if outside of the game boundaries
            # or if there is already a piece there
            if clamp([x,y]) or matrix[x][y] > 0: return False

    pos[0] += direction[0]
    pos[1] += direction[1]        
    return True

def drop(matrix, shape, pos):
    """ drop a piece by repeatedly going down one unit"""
    while move(matrix, shape, pos, (0,1)): pass
    
def add(matrix, shape, pos, color):
    counter=0
    touched_rows = []
    for i in range(4):
        for j in range(4):
            if shape[i][j] == 0: continue
            counter += 1
            x = pos[0] + i
            y = pos[1] + j
            matrix[x][y] = color+1
            # keep track of which rows are impacted
            if y not in touched_rows: touched_rows.append(y)

    completed_rows = []
    for row in touched_rows:
        for i in range(mult):
            if matrix[i][row] == 0: break
        else: completed_rows.append(row)

    for row in completed_rows:        
        for j in range(row,0,-1):
            for i in range(mult): 
                matrix[i][j] = matrix[i][j-1]
    
    # zero out rows that have been cleared at the top
    for i in range(mult):
        for j in range(len(completed_rows)):
            matrix[i][j]=0
    return counter

    

# define a main function
def main():

    # init possible Tetris shapes
    shapes = buildShapes()

    # initialize the pygame module
    pygame.init()
    # load and set the logo
    pygame.display.set_caption("Tetris")
     
    # create a square surface on screen that has the desired size
    width = mult*size
    height = mult*size
    screen = pygame.display.set_mode((width,height))

    # represent board as a 2d array, 0 means empty, else color+1
    row = [0]*mult
    matrix = [list(row) for i in range(mult)]

    # pick a random shape and position to start game
    random.seed()
    shape = random.randint(0,len(shapes)-1)
    pos = [random.randint(0,mult-5), 0]
    orient = 0    

    # main loop
    iteration = 0
    score = 0
    lost = False
    paused = False    
    running = True    
    while running:
        # event handling, gets all event from the event queue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
            elif event.type == pygame.KEYDOWN:
                if  event.key == 27:  # escape
                    running = False
                    break

                if lost: break

                if event.key == 112:  # p
                    paused = not paused
                elif event.key == 104:  # h
                    # display help message
                    font = pygame.font.SysFont('bitstreamverasans',15) 
                    line1 = font.render("h: help - p: pause",1,(255,255,255))
                    line2 = font.render("z: rotate counterclockwise - x: rotate clockwise",1,(255,255,255))
                    line3 = font.render("space: drop - arrow keys: move",1,(255,255,255))
                    # black screen
                    screen.fill((0,0,0))
                    screen.blit(line1,(0,0))
                    screen.blit(line2,(0, size*mult/6))
                    screen.blit(line3,(0, 2*size*mult/6))
                    pygame.display.flip()
                    # and pause the game
                    paused = True

                # don't move the piece if on pause
                if paused: break
                                
                if event.key == 276:  # left arrow
                    move(matrix, rotateShape(shapes[shape],orient), pos, (-1,0))
                elif event.key == 275:# right arrow
                    move(matrix,rotateShape(shapes[shape],orient), pos, (1,0))
                elif event.key == 122:# z
                    if rotate(matrix,shapes[shape], pos, orient, -1):
                        orient -= 1
                elif event.key == 120:# x
                    if rotate(matrix,shapes[shape],  pos, orient, 1):
                        orient += 1
                elif event.key == 32: # space bar
                    drop(matrix, rotateShape(shapes[shape],orient), pos)
                
        if paused or lost: continue

        # black screen
        screen.fill((0,0,0))

        # make copy of current matrix
        display_matrix=[list(matrix[i]) for i in range(mult)]
        
        # add current shape
        add(display_matrix, rotateShape(shapes[shape],orient), pos,  shape)

        # display matrix
        displayMatrix(screen, display_matrix)

        # display score Top Left corner
        font = pygame.font.SysFont('bitstreamverasans',15) 
        score_text = font.render(str(int(score)),1,(255,255,255))
        screen.blit(score_text,(0,0))

        pygame.time.delay(iteration_speed)
        prev_round = iteration // min_speed
        iteration += 1 
        cur_round = iteration // min_speed

        # swap display buffer
        pygame.display.flip()

        # move piece down (at a slower rate than the iteration rate)
        if prev_round == cur_round: continue

        # test whether we can still move that piece down
        if not move(matrix, rotateShape(shapes[shape],orient), pos, (0,1)):

            # keep track of score
            score += add(matrix, rotateShape(shapes[shape],orient), pos, shape)
            
            # pick a random new shape and position with default orientation
            shape = random.randint(0,len(shapes)-1)        
            pos = [random.randint(0,mult-5), 0]
            orient = 0

            # test whether the game is lost
            if not move(matrix, shapes[shape], pos):
                lost = True
    
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()