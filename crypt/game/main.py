import pygame
import random
import json
import sys
from models import *
from engine import *



def loadInCardData(json_file):
  '''
  Load in player deck and enemy deck from the json file

  Load in player name, enemy name, player health, 
  enemy health, player strength, enemy strength, 
  player intelligence, enemy intelligence, player dexterity,
  enemy dexterity, player image path, enemy image path

  Instantiate gameEngine with the above data
  
  '''
  with open(json_file) as f:
    data = json.load(f)
  # get player and enemy decks first
  Deck = []
  for card in data['deck']:
    Deck.append(Card(card['type'],card['value'],card['image_path']))

gameEngine = None
GAMESTAKE = 0
CARDSTOWIN = []

n = len(sys.argv)
player_health = int(sys.argv[1])
enemy_health = int(sys.argv[2])
player_strength = int(sys.argv[3])
enemy_strength = int(sys.argv[4])
player_intelligence = int(sys.argv[5])
enemy_intelligence = int(sys.argv[6])
player_dexterity = int(sys.argv[7])
enemy_dexterity = int(sys.argv[8])
player_name = sys.argv[9]
player_token = sys.argv[10]
enemy_id = int(sys.argv[11])
enemy_name = sys.argv[12]
player_image_path = sys.argv[13]
enemy_image_path = sys.argv[14]
GAMESTAKE = float(sys.argv[15])
player_deck = Deck([Card(Types.ATTACK,Values.STRENGTH,r"images/Arcane Smite.png")]*10 + [Card(Types.ATTACK,Values.INTELLIGENCE,r"images/Chain Lightning.png")]*5 
                  + [Card(Types.DODGE,Values.DEXTERITY,r"images/Blink Step.png")]*5 + [Card(Types.DEFENSE,Values.STRENGTH,r"images/Mystic Barrier.png")]*5 + 
                  [Card(Types.DEFENSE,Values.INTELLIGENCE,r"images/Spell Reflection.png")]*5)
enemy_deck = Deck([Card(Types.ATTACK,Values.INTELLIGENCE,r"images/Arcane Nova.png")]*10 + [Card(Types.DODGE,Values.DEXTERITY,r"images/Ethereal Dodge.png")]*10
                 + [Card(Types.DEFENSE,Values.INTELLIGENCE,r"images/Elemental Aegis.png")]*10)
CARDSTOWIN = [Card(Types.ATTACK, Values.INTELLIGENCE, r"images/Arcane Nova.png"), Card(Types.DODGE,Values.DEXTERITY,r"images/Ethereal Dodge.png"), Card(Types.DEFENSE,Values.INTELLIGENCE,r"images/Elemental Aegis.png")]
gameEngine = GameEngine(player_deck,enemy_deck, player_name, enemy_name, 
                        player_health, enemy_health, 
                        player_strength, enemy_strength, 
                        player_intelligence, enemy_intelligence, 
                        player_dexterity, enemy_dexterity, 
                        player_image_path, enemy_image_path, 
                        player_token, enemy_id)



pygame.init()
# Set Up
info = pygame.display.Info() 
screen_width,screen_height = info.current_w,info.current_h
window_width,window_height = screen_width-10,screen_height-50
window = pygame.display.set_mode((window_width,window_height))
algocrypt_icon = pygame.image.load('images/logo.png')

pygame.display.set_icon(algocrypt_icon)
pygame.display.set_caption("AlgoCrypt")


PLAYERHEALTH = gameEngine.player.health
ENEMYHEALTH = gameEngine.enemy.health

# Image used for draw and discard piles
cardBack = pygame.image.load('images/REALCARDBACK.png')
cardBack = pygame.transform.scale(cardBack, (int(238*0.6), int(332*0.6)))



def renderGame(window):
  window.fill((12,9,13))
  font = pygame.font.SysFont('arial',20, True)

  if (gameEngine.state == GameState.WIN):
    font = pygame.font.SysFont('arial',50, True)
    winText = font.render("You Win!", True, (8,126,139))
    window.blit(winText, (window.get_width()/2 - winText.get_width()/2, window.get_height()/2 - winText.get_height()/2))
    window.blit(gameEngine.enemy.image, (700, 600))
    gameEngine.enemy.replenishDeck()
    for i in range(3):
      window.blit(CARDSTOWIN[i].image, (700 + ((i+2)*100), 600))
    gameEngine.state = GameState.ENDED
    return
  elif (gameEngine.state == GameState.LOSE):
    font = pygame.font.SysFont('arial',50, True)
    loseText = font.render("You Lose " + str(GAMESTAKE) + " CRPT!", True, (200,29,37))
    window.blit(loseText, (window.get_width()/2 - loseText.get_width()/2, window.get_height()/2 - loseText.get_height()/2))
    gameEngine.state = GameState.ENDED
    return
  


  if (gameEngine.state == GameState.STARTUP):
    startPlayText = font.render("Press The 'D' Key To Draw", True, (191,215,234))
    window.blit(startPlayText, (950,450))

  #player image
  window.blit(gameEngine.player.image, (100, 600))
  #player health
  healthText = font.render("Health: " + str(gameEngine.player.health) + "/" + str(PLAYERHEALTH), True, (200,29,37))
  window.blit(healthText, (100, 570))
  pygame.draw.rect(window, (200,29,37), (100, 550, 180, 10))
  pygame.draw.rect(window, (0,128,0), (100, 550, max(180 - (2 * (PLAYERHEALTH - gameEngine.player.health)),2), 10))
  #player attack and defense
  physAttackText = font.render("Phys Att.: " + str(gameEngine.player.physDamage), True, (200,29,37))
  physDefenseText = font.render("Phys Def.: " + str(gameEngine.player.physDefense), True, (200,29,37))
  magAttackText = font.render("Mag Att.: " + str(gameEngine.player.magDamage), True, (200,29,37))
  magDefenseText = font.render("Mag Def.: " + str(gameEngine.player.magDefense), True, (200,29,37))
  window.blit(physAttackText, (300, 790))
  window.blit(physDefenseText, (300, 810))
  window.blit(magAttackText, (300, 830))
  window.blit(magDefenseText, (300, 850))
  #player damage
  if (gameEngine.state == GameState.DONEPLAY):
    damageText = font.render("-" + str(gameEngine.player.damage), True, (200,29,37))
    window.blit(damageText, (300, 750))

  text = font.render(gameEngine.player.name, True, (191,215,234))
  window.blit(text, (100, 900))

  #enemy image
  window.blit(gameEngine.enemy.image, (100, 100))
  #enemy health
  healthText = font.render("Health: " + str(gameEngine.enemy.health) + "/" + str(ENEMYHEALTH), True, (200,29,37))
  window.blit(healthText, (100, 370))
  pygame.draw.rect(window, (200,29,37), (100, 400, 180, 10))
  pygame.draw.rect(window, (0,128,0), (100, 400, max(180 - (2 * (ENEMYHEALTH - gameEngine.enemy.health)),2), 10))
  #enemy attack and defense
  physAttackText = font.render("Phys Att.: " + str(gameEngine.enemy.physDamage), True, (200,29,37))
  magAttackText = font.render("Mag Att.: " + str(gameEngine.enemy.magDamage), True, (200,29,37))
  physDefenseText = font.render("Phys Def.: " + str(gameEngine.enemy.physDefense), True, (200,29,37))
  magDefenseText = font.render("Mag Def.: " + str(gameEngine.enemy.magDefense), True, (200,29,37))
  window.blit(physAttackText, (300, 290))
  window.blit(physDefenseText, (300, 310))
  window.blit(magAttackText, (300, 330))
  window.blit(magDefenseText, (300, 350))
  #enemy damage
  if (gameEngine.state == GameState.DONEPLAY):
    damageText = font.render("-" + str(gameEngine.enemy.damage), True, (200,29,37))
    window.blit(damageText, (300, 250))
  text = font.render(gameEngine.enemy.name, True, (191,215,234))
  window.blit(text, (100, 50))

  # Draw piles
  drawText = font.render("Draw Pile: " + str(gameEngine.player.deck.length()), True, (8,126,139))
  window.blit(drawText, (500, 800))
  window.blit(cardBack, (500, 600)) # Player
  # Player stats
  userText1 = font.render("User Stats: ", True, (255,90,95))
  userText2 = font.render("Strength: " + str(gameEngine.player.strength), True, (255,90,95))
  userText3 = font.render("Intelligence: " + str(gameEngine.player.intelligence), True, (255,90,95))
  userText4 = font.render("Dexterity: " + str(gameEngine.player.dexterity), True, (255,90,95))
  window.blit(userText1, (300, 600))
  window.blit(userText2, (300, 650))
  window.blit(userText3, (300, 675))
  window.blit(userText4, (300, 700))

  window.blit(cardBack, (500, 100)) # Enemy
  # Enemy stats
  enemyText1 = font.render("Enemy Stats: ", True, (255,90,95))
  enemyText2 = font.render("Strength: " + str(gameEngine.enemy.strength), True, (255,90,95))
  enemyText3 = font.render("Intelligence: " + str(gameEngine.enemy.intelligence), True, (255,90,95))
  enemyText4 = font.render("Dexterity: " + str(gameEngine.enemy.dexterity), True, (255,90,95))  
  window.blit(enemyText1, (300, 100))
  window.blit(enemyText2, (300, 150))
  window.blit(enemyText3, (300, 175))
  window.blit(enemyText4, (300, 200))

  # Discard piles
  window.blit(cardBack, (1700, 600))
  discardText = font.render("Discard Pile: " + str(gameEngine.player.discard.length()), True, (8,126,139))
  window.blit(discardText, (1700, 800))

  window.blit(cardBack, (1700, 100))

  # Player hand
  if (gameEngine.state == GameState.DRAWING or gameEngine.state == GameState.INPLAY):
    cardNumberText1 = font.render(str(1), True, (8,126,139))
    cardNumberText2 = font.render(str(2), True, (8,126,139))
    cardNumberText3 = font.render(str(3), True, (8,126,139))
    cardNumberText4 = font.render(str(4), True, (8,126,139))
    cardNumberText5 = font.render(str(5), True, (8,126,139))
    window.blit(cardNumberText1, (864, 900))
    window.blit(cardNumberText2, (1014, 900))
    window.blit(cardNumberText3, (1164, 900))
    window.blit(cardNumberText4, (1314, 900))
    window.blit(cardNumberText5, (1464, 900))
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
    if (gameEngine.enemy.hand[0] != None and type(gameEngine.enemy.hand[0]) == Card):
      window.blit(cardBack, (800, 0))
    if (gameEngine.enemy.hand[1] != None and type(gameEngine.enemy.hand[1]) == Card):
      window.blit(cardBack, (950, 0))
    if (gameEngine.enemy.hand[2] != None and type(gameEngine.enemy.hand[2]) == Card):
      window.blit(cardBack, (1100, 0))
    if (gameEngine.enemy.hand[3] != None and type(gameEngine.enemy.hand[3]) == Card):
      window.blit(cardBack, (1250, 0))
    if (gameEngine.enemy.hand[4] != None and type(gameEngine.enemy.hand[4]) == Card):
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

def damageCalc(player, enemy):
  damageToPlayer = max(0, enemy.physDamage - player.physDefense) + max(0, enemy.magDamage - player.magDefense)
  damageToEnemy = max(0, player.physDamage - enemy.physDefense) + max(0, player.magDamage - enemy.magDefense)

  player.damage = damageToPlayer
  enemy.damage = damageToEnemy

  player.health = max(0,player.health - player.damage)
  enemy.health = max(0,enemy.health - enemy.damage)




run = True
while run:
  key = None; 
  
  if (gameEngine.state == GameState.DONEPLAY):
    pygame.time.delay(2000)
    gameEngine.player.resetDamage()
    gameEngine.enemy.resetDamage()
    if (gameEngine.enemy.health==0):
      gameEngine.state = GameState.WIN
    elif (gameEngine.player.health==0):
      gameEngine.state = GameState.LOSE
    else:
      gameEngine.state = GameState.STARTUP

  if (gameEngine.state == GameState.INPLAY):
    pygame.time.delay(3000)
    gameEngine.player.action(gameEngine.enemy)
    gameEngine.enemy.action()
    damageCalc(gameEngine.player, gameEngine.enemy)
    gameEngine.state = GameState.DONEPLAY


  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if (gameEngine.state == GameState.STARTUP or gameEngine.state == GameState.DRAWING) and event.type == pygame.KEYDOWN:
      key = event.key
  if (gameEngine.state == GameState.ENDED):
    continue
  
  gameEngine.play(key)
  renderGame(window)
  pygame.display.update()

 