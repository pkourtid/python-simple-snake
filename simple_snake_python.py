# Written by Panagiotis Kourtidis

import pygame
from pygame.locals import *
from pygame import mixer
import random

# =============================================================================
# We need some helper classes

# This simpler timer class will be use to time certain events
# Not super accurate when used within the event loop but good enough
# for simple games like this

class clsSimpleTimer:
    
    def __init__(self):
        self.start_ticks = pygame.time.get_ticks()

    def resetTimer(self):
        self.start_ticks = pygame.time.get_ticks()
    
    def checkTimePassed(self, intMsCheck):
        
        intMsPassed = (int(pygame.time.get_ticks()) - int(self.start_ticks))
        
        if (intMsPassed > intMsCheck):
            return True
        else:
            return False


class clsBoardObject:
    mushroom = False
    tile = "imgBlock0"
    
class clsSnakeObject:
    x=0
    y=0
    active=False
    

# =============================================================================
# Initialize pygame
# =============================================================================

pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Simple Snake')
screen = pygame.display.set_mode((500, 500), RESIZABLE)
# =============================================================================

# =============================================================================
# Game variables
# =============================================================================

# Load resources

dicResources = {}

dicResources["imgBlock0"] = pygame.image.load("graphics/block_0.png")
dicResources["imgBlock1"] = pygame.image.load("graphics/block_1.png")
dicResources["imgBlock2"] = pygame.image.load("graphics/block_2.png")
dicResources["imgBlock3"] = pygame.image.load("graphics/block_3.png")
dicResources["imgStart"] = pygame.image.load("graphics/startgame.png")
dicResources["imgTitle"] = pygame.image.load("graphics/title.png")

# Some sounds for the game
sndEatMushroom = pygame.mixer.Sound("sounds/eat.mp3")
sndGameOver = pygame.mixer.Sound("sounds/gameover.mp3")
sndWhoosh = pygame.mixer.Sound("sounds/whoosh.mp3")

decScaleWidth = 1.0
decScaleHeight = 1.0
decScaleGame = 1.0;
decOffsetWidth = 0.0;
decOffsetHeight = 0.0;

intGameWidth = 250.0
intGameHeight = 440.0
white = (255, 255, 255)
black = (0, 0, 0)

intWorldHeight = 37;
intWorldWidth = 24;
intMaxSnakeLength = 300;

intBlockDimension = 10;
intBoardXOffset = 5;

blnShowMessage = True
tmrPressSpace = clsSimpleTimer()
tmrMoveSnake = clsSimpleTimer()

intGameState = 0
arrGameBoard = [0] * intWorldWidth # Holds block information

for i in range(len(arrGameBoard)):
    arrGameBoard[i] = [0] * intWorldHeight
    
for i in range(len(arrGameBoard)):
    for j in range(len(arrGameBoard[i])):
        arrGameBoard[i][j] = clsBoardObject()
        
arrGameSnake = [0] * intMaxSnakeLength

for i in range(len(arrGameSnake)):
    arrGameSnake[i] = clsSnakeObject()
            
intSnakeDirection = 0
intGameScore = 0

blnSnakeMove = False


# =============================================================================
# Define game functions
# =============================================================================

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# resetGame() resets all variables as needed for the game to restart

def resetGame():
    
    global intSnakeDirection, tmrPressSpace, tmrMoveSnake
    global intGameScore, arrGameBoard, arrGameSnake, blnSnakeMove
    
    tmrPressSpace.resetTimer()
    tmrMoveSnake.resetTimer()
    
    intGameScore = 0;
	
    for i in range(len(arrGameBoard)):
        for j in range(len(arrGameBoard[i])):
            arrGameBoard[i][j].mushroom = False
            arrGameBoard[i][j].tile = "imgBlock0"
        
    for i in range(len(arrGameSnake)):
        arrGameSnake[i].x = 0
        arrGameSnake[i].y = 0
        arrGameSnake[i].active = False
    
    for i in range(5):
        y = random.randint(0, 36)
        x = random.randint(0, 23)
        arrGameBoard[x][y].mushroom = True
        arrGameBoard[x][y].tile = "imgBlock2"
    
    arrGameSnake[0].x = 12;
    arrGameSnake[0].y = 18;
	
    arrGameSnake[1].x = 11;
    arrGameSnake[1].y = 18;
    
    arrGameSnake[2].x = 10;
    arrGameSnake[2].y = 18;
    
    arrGameSnake[3].x = 9;
    arrGameSnake[3].y = 18;
	
    arrGameSnake[0].active = True;
    arrGameSnake[1].active = True;
    arrGameSnake[2].active = True;
    arrGameSnake[3].active = True;
	
    intSnakeDirection = 0;
	
    blnSnakeMove = False;

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Create a function to draw the playing area

def drawSimpleSnakePlayArea():
    for i in range(len(arrGameBoard)):
        for j in range(len(arrGameBoard[i])):
            if (arrGameBoard[i][j].mushroom == True):
                drawImage(dicResources[arrGameBoard[i][j].tile], (i*intBlockDimension) + intBoardXOffset, (j*intBlockDimension) + intBoardXOffset, intBlockDimension+2, intBlockDimension+2) 
            else:
                drawImage(dicResources[arrGameBoard[i][j].tile], (i*intBlockDimension) + intBoardXOffset, (j*intBlockDimension) + intBoardXOffset, intBlockDimension+2, intBlockDimension+2) 
    
    for i in range(intMaxSnakeLength):
        if (arrGameSnake[i].active):
            if (i == 0):
                drawImage(dicResources["imgBlock3"], (arrGameSnake[i].x*intBlockDimension) + intBoardXOffset, (arrGameSnake[i].y*intBlockDimension) + intBoardXOffset, intBlockDimension+2, intBlockDimension+2)
            else:
                if (not(arrGameSnake[i].x == arrGameSnake[0].x and arrGameSnake[i].y == arrGameSnake[0].y)):
                    drawImage(dicResources["imgBlock1"], (arrGameSnake[i].x*intBlockDimension) + intBoardXOffset, (arrGameSnake[i].y*intBlockDimension) + intBoardXOffset, intBlockDimension+2, intBlockDimension+2)
        else:
            break

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# When the screen is resized this function is triggered
# We calculate some variables to help up scale and center the whole game 
          
def resize_display():
    
    #calculate the scale to be used and the offset from center
    
    global decScaleWidth, decScaleHeight, decScaleGame, decOffsetWidth, decOffsetHeight
    
    # get the screen size
    x, y = screen.get_size()

    decScaleWidth = float(x) / intGameWidth
    decScaleHeight = float(y) / intGameHeight
    
	# set a few scaling variables
    if (decScaleWidth < decScaleHeight):
        decScaleGame = decScaleWidth
        decOffsetHeight = (y - (intGameHeight*decScaleGame))/2
        decOffsetWidth = 0.0
    else:
        decScaleGame = decScaleHeight;
        decOffsetWidth = (x - (intGameWidth*decScaleGame))/2
        decOffsetHeight = 0.0

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Create a function to draw an image on the canvas honoring the scale

def drawImage(imgObject, intOffsetX, intOffsetY, intWidth, intHeight):
    # screen.blit(imgObject, (100,100))
    imgObjectResized = pygame.transform.scale(imgObject, (intWidth*decScaleGame,intHeight*decScaleGame))
    screen.blit(imgObjectResized, (decOffsetWidth + (intOffsetX*decScaleGame), decOffsetHeight + (intOffsetY*decScaleGame)))

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# The main game logic

def moveSnake():
    global blnSnakeMove, intGameScore, arrGameSnake, arrGameBoard, intGameState
    
    if (tmrMoveSnake.checkTimePassed(160)):
        
        tmrMoveSnake.resetTimer()
        
        for i in range(intMaxSnakeLength - 1, 0, -1):
            if (arrGameSnake[i].active == True):
                arrGameSnake[i].x = arrGameSnake[i-1].x
                arrGameSnake[i].y = arrGameSnake[i-1].y
        
        if (intSnakeDirection == 0):
            arrGameSnake[0].x += 1
        elif (intSnakeDirection == 1):
            arrGameSnake[0].y -= 1
        elif (intSnakeDirection == 2):
            arrGameSnake[0].y += 1
        elif (intSnakeDirection == 3):
            arrGameSnake[0].x -= 1
        
        # Check if we hit the wall
        if ((arrGameSnake[0].x > (intWorldWidth - 1)) or (arrGameSnake[0].y > (intWorldHeight - 1)) or (arrGameSnake[0].x < 0) or (arrGameSnake[0].y < 0)):
            # Hit the wall
            pygame.mixer.Sound.play(sndGameOver)
            intGameState = 0
        else:
            # Check if we ate a mushroom
            if (arrGameBoard[arrGameSnake[0].x][arrGameSnake[0].y].mushroom == True):
                # Eat it!
                pygame.mixer.Sound.play(sndEatMushroom)
                arrGameBoard[arrGameSnake[0].x][arrGameSnake[0].y].mushroom = False
                arrGameBoard[arrGameSnake[0].x][arrGameSnake[0].y].tile = "imgBlock0"
                intGameScore = intGameScore + 1;
                
                # Grow a new mushroom
                y = random.randint(0, 36)
                x = random.randint(0, 23)
                arrGameBoard[x][y].mushroom = True
                arrGameBoard[x][y].tile = "imgBlock2"
                
                # Grow
                for i in range(intMaxSnakeLength):
                    if (arrGameSnake[i].active == False):
                        arrGameSnake[i].x = -100
                        arrGameSnake[i].y = -100
                        arrGameSnake[i].active = True
                        break
            
            # check if we hit our body
            for i in range (intMaxSnakeLength - 1, 0, -1):
                if (arrGameSnake[i].active == True and arrGameSnake[i].x == arrGameSnake[0].x and arrGameSnake[i].y == arrGameSnake[0].y):
                    # We hit our body!
                    pygame.mixer.Sound.play(sndGameOver)
                    intGameState = 0  
            
        blnSnakeMove = False
		

# =============================================================================
# Starting the game loop
# =============================================================================

blnRunning = True
resize_display()

while blnRunning:

    # Clear the Screen
    screen.fill(black)
    
    # Check the game state
 
    # **************************
    # Ready to play the game
    if (intGameState == 0):
        # Press space to start the game
        drawSimpleSnakePlayArea()
        
        drawImage(dicResources["imgTitle"], 0, 375, 250, 40)
        
        # Logic to show/hide the start game message
        if ((blnShowMessage and tmrPressSpace.checkTimePassed(800)) or (not(blnShowMessage) and tmrPressSpace.checkTimePassed(300))):
        # if  tmrPressSpace.checkTimePassed(800):
            pygame.mixer.Sound.play(sndWhoosh)
            blnShowMessage = not(blnShowMessage)
            tmrPressSpace.resetTimer()
        
        if (blnShowMessage):
            drawImage(dicResources["imgStart"], 25, 170, 200, 40)
    
    # **************************
    # We are now playing the game
    elif (intGameState == 1):
        drawSimpleSnakePlayArea()
        moveSnake()
        drawImage(dicResources["imgTitle"], 0, 375, 250, 40)
        
    for event in pygame.event.get():
        if event.type == QUIT:
            blnRunning = False
        elif event.type == pygame.KEYDOWN:
            if (intGameState == 0):
                if (event.key == pygame.K_SPACE):
                    resetGame()
                    intGameState = 1
            elif (intGameState == 1):
                if (blnSnakeMove == False):
                    
                    if (event.key == pygame.K_DOWN):
                        if (intSnakeDirection != 1 and intSnakeDirection != 2):
                            intSnakeDirection = 2
                            blnSnakeMove = True
                    if (event.key == pygame.K_UP):
                        if (intSnakeDirection != 2 and intSnakeDirection != 1):
                            intSnakeDirection = 1
                            blnSnakeMove = True
                    if (event.key == pygame.K_RIGHT):
                        if (intSnakeDirection != 3 and intSnakeDirection != 0):
                            intSnakeDirection = 0
                            blnSnakeMove = True
                    if (event.key == pygame.K_LEFT):
                        if (intSnakeDirection != 0 and intSnakeDirection != 3):
                            intSnakeDirection = 3
                            blnSnakeMove = True
            
        elif event.type == VIDEORESIZE:
            resize_display()
        
    pygame.display.update()
    
pygame.quit()

        
