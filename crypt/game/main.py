import pygame
from models import *
from engine import *

pygame.init()
# Set Up
info = pygame.display.Info() 
screen_width,screen_height = info.current_w,info.current_h
window_width,window_height = screen_width-10,screen_height-50
window = pygame.display.set_mode((window_width,window_height))
algocrypt_icon = pygame.image.load('images/logo.png')
pygame.display.set_icon(algocrypt_icon)
pygame.display.set_caption("AlgoCrypt")
font = pygame.font.SysFont('arial',20, True)


playerDeck = Deck([Card(Types.ATTACK,2,"images/BACK.png")]*30)
enemyDeck = Deck([Card(Types.ATTACK,2,"images/BACK.png")]*30)
gameEngine = GameEngine(playerDeck,enemyDeck,
                        "PalaMAN","Gandalf The Grey",
                        playerHealth=100,enemyHealth=100,
                        playerStrength=5,enemyStrength=2,
                        playerIntelligence=2,enemyIntelligence=10,
                        playerDexterity=4,enemyDexterity=2,
                        playerImagePath="images/pala.png",enemyImagePath="images/wizard.png")
PLAYERHEALTH = gameEngine.player.health
ENEMYHEALTH = gameEngine.enemy.health

# Image used for draw and discard piles
cardBack = pygame.image.load('images/BACK.png')
cardBack = pygame.transform.scale(cardBack, (int(238*0.6), int(332*0.6)))

def renderGame(window):
  window.fill((1,50,32))

  if (gameEngine.state == GameState.STARTUP):
    startPlayText = font.render("Press The Space Bar To Draw", True, (144, 238, 144))
    window.blit(startPlayText, (950,450))

  #player image
  window.blit(gameEngine.player.image, (100, 600))
  #player health
  healthText = font.render("Health: " + str(gameEngine.player.health) + "/" + str(PLAYERHEALTH), True, (255,0,0), (64,47,29))
  window.blit(healthText, (300, 825))

  text = font.render(gameEngine.player.name, True, (0,0,0))
  window.blit(text, (100, 900))

  #enemy image
  window.blit(gameEngine.enemy.image, (100, 100))
  #enemy health
  healthText = font.render("Health: " + str(gameEngine.enemy.health) + "/" + str(ENEMYHEALTH), True, (255,0,0), (64,47,29))
  window.blit(healthText, (300, 325))
  text = font.render(gameEngine.enemy.name, True, (0,0,0))
  window.blit(text, (100, 50))

  # Draw piles
  drawText = font.render("Draw Pile: " + str(gameEngine.player.deck.length()), True, (0,0,255))
  window.blit(drawText, (500, 800))
  window.blit(cardBack, (500, 600)) # Player
  # Player stats
  userText1 = font.render("User Stats: ", True, (0,0,0))
  userText2 = font.render("Strength: " + str(gameEngine.player.strength), True, (0,0,0))
  userText3 = font.render("Intelligence: " + str(gameEngine.player.intelligence), True, (0,0,0))
  userText4 = font.render("Dexterity: " + str(gameEngine.player.dexterity), True, (0,0,0))
  window.blit(userText1, (300, 600))
  window.blit(userText2, (300, 650))
  window.blit(userText3, (300, 675))
  window.blit(userText4, (300, 700))

  window.blit(cardBack, (500, 100)) # Enemy
  # Enemy stats
  enemyText1 = font.render("Enemy Stats: ", True, (0,0,0))
  enemyText2 = font.render("Strength: " + str(gameEngine.enemy.strength), True, (0,0,0))
  enemyText3 = font.render("Intelligence: " + str(gameEngine.enemy.intelligence), True, (0,0,0))
  enemyText4 = font.render("Dexterity: " + str(gameEngine.enemy.dexterity), True, (0,0,0))  
  window.blit(enemyText1, (300, 100))
  window.blit(enemyText2, (300, 150))
  window.blit(enemyText3, (300, 175))
  window.blit(enemyText4, (300, 200))

  # Discard piles
  window.blit(cardBack, (1700, 600))
  discardText = font.render("Discard Pile: " + str(gameEngine.player.discard.length()), True, (0,0,255))
  window.blit(discardText, (1700, 800))

  window.blit(cardBack, (1700, 100))

  # Player hand
  if (gameEngine.state == GameState.DRAWING or gameEngine.state == GameState.INPLAY):
    if (gameEngine.player.hand[0] != None and type(gameEngine.player.hand[0]) == Card):
      window.blit(gameEngine.player.hand[0].image, (800, 700))
    if (gameEngine.player.hand[1] != None and type(gameEngine.player.hand[1]) == Card):
      window.blit(gameEngine.player.hand[1].image, (950, 700))
    if (gameEngine.player.hand[2] != None and type(gameEngine.player.hand[2]) == Card):
      window.blit(gameEngine.player.hand[2].image, (1100, 700))
    if (gameEngine.player.hand[3] != None and type(gameEngine.player.hand[3]) == Card):
      window.blit(gameEngine.player.hand[3].image, (1250, 700))
    if (gameEngine.player.hand[4] != None and type(gameEngine.player.hand[4]) == Card):
      window.blit(gameEngine.player.hand[4].image, (1400, 700))

  # Enemy hand
  if (gameEngine.state == GameState.DRAWING or gameEngine.state == GameState.INPLAY):
    if (gameEngine.enemy.hand[0] != None):
      window.blit(cardBack, (800, 0))
    if (gameEngine.enemy.hand[1] != None):
      window.blit(cardBack, (950, 0))
    if (gameEngine.enemy.hand[2] != None):
      window.blit(cardBack, (1100, 0))
    if (gameEngine.enemy.hand[3] != None):
      window.blit(cardBack, (1250, 0))
    if (gameEngine.enemy.hand[4] != None):
      window.blit(cardBack, (1400, 0))

  # Player played cards
  if (gameEngine.state == GameState.DRAWING or gameEngine.state == GameState.INPLAY):
    if (gameEngine.player.play[0] != None and type(gameEngine.player.play[0]) == Card):
      window.blit(gameEngine.player.play[0].image, (950, 450))
    if (gameEngine.player.play[1] != None and type(gameEngine.player.play[1]) == Card):
      window.blit(gameEngine.player.play[1].image, (1100, 450))
    if (gameEngine.player.play[2] != None and type(gameEngine.player.play[2]) == Card):
      window.blit(gameEngine.player.play[2].image, (1250, 450))

  # Enemy played cards
  if (gameEngine.state == GameState.INPLAY):
    if (gameEngine.enemy.play[0] != None):
      window.blit(gameEngine.enemy.play[0].image, (950, 250))
    if (gameEngine.enemy.play[1] != None):
      window.blit(gameEngine.enemy.play[1].image, (1100, 250))
    if (gameEngine.enemy.play[2] != None):
      window.blit(gameEngine.enemy.play[2].image, (1250, 250))




run = True
while run:
  key = None; 
  if (gameEngine.state == GameState.INPLAY):
    pygame.time.delay(3000)
    gameEngine.player.action()
    gameEngine.enemy.action()
    gameEngine.state = GameState.STARTUP


  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if (gameEngine.state == GameState.STARTUP or gameEngine.state == GameState.DRAWING) and event.type == pygame.KEYDOWN:
      key = event.key

  
  gameEngine.play(key)
  renderGame(window)
  pygame.display.update()

  # if gameEngine.state == GameState.SNAPPING:
  #   pygame.time.delay(3000)
  #   gameEngine.state = GameState.PLAYING