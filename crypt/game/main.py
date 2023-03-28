import pygame
from models import *
from engine import *

pygame.init()
bounds = (1024, 768)
window = pygame.display.set_mode(bounds)
pygame.display.set_caption("AlgoCrypt")

gameEngine = SnapEngine()

enemyImage = pygame.image.load('images/wizard.png')
enemyImage = pygame.transform.scale(enemyImage, (int(238*0.8), int(332*0.8)))

playerImage = pygame.image.load('images/pala.png')
playerImage = pygame.transform.scale(playerImage, (int(238*0.8), int(332*0.8)))

cardBack = pygame.image.load('images/BACK.png')
cardBack = pygame.transform.scale(cardBack, (int(238*0.6), int(332*0.6)))

def renderGame(window):
  window.fill((1,50,32))
  font = pygame.font.SysFont('arial',20, True)

  #player image
  window.blit(playerImage, (100, 600))
  #player health
  pygame.draw.rect(window, (255,0,0), (100, 550, 190, 10)) 
  pygame.draw.rect(window, (0,128,0), (100, 550, 190, 10)) 

  #enemy image
  window.blit(enemyImage, (100, 100))
  #enemy health
  pygame.draw.rect(window, (255,0,0), (100, 400, 190, 10)) 
  pygame.draw.rect(window, (0,128,0), (100, 400, 190, 10)) 

  # Draw piles
  window.blit(cardBack, (500, 600)) # Player
  # Player stats
  userText1 = font.render("User Stats: ", True, (0,0,0))
  userText2 = font.render("Strength: ", True, (0,0,0))
  userText3 = font.render("Intelligence: ", True, (0,0,0))
  userText4 = font.render("Dexterity: ", True, (0,0,0))
  window.blit(userText1, (300, 600))
  window.blit(userText2, (300, 650))
  window.blit(userText3, (300, 675))
  window.blit(userText4, (300, 700))

  window.blit(cardBack, (500, 100)) # Enemy
  # Enemy stats
  enemyText1 = font.render("Enemy Stats: ", True, (0,0,0))
  enemyText2 = font.render("Strength: ", True, (0,0,0))
  enemyText3 = font.render("Intelligence: ", True, (0,0,0))
  enemyText4 = font.render("Dexterity: ", True, (0,0,0))  
  window.blit(enemyText1, (300, 100))
  window.blit(enemyText2, (300, 150))
  window.blit(enemyText3, (300, 175))
  window.blit(enemyText4, (300, 200))

  # Discard piles
  window.blit(cardBack, (1700, 600))
  window.blit(cardBack, (1700, 100))

  # Player hand
  window.blit(cardBack, (800, 700))
  window.blit(cardBack, (950, 700))
  window.blit(cardBack, (1100, 700))
  window.blit(cardBack, (1250, 700))
  window.blit(cardBack, (1400, 700))

  # Enemy hand
  window.blit(cardBack, (800, 0))
  window.blit(cardBack, (950, 0))
  window.blit(cardBack, (1100, 0))
  window.blit(cardBack, (1250, 0))
  window.blit(cardBack, (1400, 0))

  # Player played cards
  window.blit(cardBack, (950, 450))
  window.blit(cardBack, (1100, 450))
  window.blit(cardBack, (1250, 450))

  # Enemy played cards
  window.blit(cardBack, (950, 250))
  window.blit(cardBack, (1100, 250))
  window.blit(cardBack, (1250, 250))
  # text = font.render(str(len(gameEngine.player1.hand)) + " cards", True, (0,0,0))
  # window.blit(text, (100, 500))

  # text = font.render(str(len(gameEngine.player2.hand)) + " cards", True, (255,255,255))
  # window.blit(text, (700, 500))

  topCard = gameEngine.pile.peek()
  if (topCard != None):
    window.blit(topCard.image, (400, 200))


  if gameEngine.state == GameState.PLAYING:
    # text = font.render(gameEngine.currentPlayer.name + " to flip", True, (255,255,255))
    # window.blit(text, (20,50))
    pass

  if gameEngine.state == GameState.SNAPPING:
    result = gameEngine.result
    if result["isSnap"] == True:
      message = "Winning Snap! by " + result["winner"].name
    else:
      message = "False Snap! by " + result["snapCaller"].name + ". " + result["winner"].name + " wins!"
    text = font.render(message, True, (255,255,255))
    window.blit(text, (20,50))

  if gameEngine.state == GameState.ENDED:
    result = gameEngine.result
    message = "Game Over! " + result["winner"].name + " wins!"
    text = font.render(message, True, (255,255,255))
    window.blit(text, (20,50))


run = True
while run:
  key = None; 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if event.type == pygame.KEYDOWN:
      key = event.key

  
  gameEngine.play(key)
  renderGame(window)
  pygame.display.update()

  if gameEngine.state == GameState.SNAPPING:
    pygame.time.delay(3000)
    gameEngine.state = GameState.PLAYING