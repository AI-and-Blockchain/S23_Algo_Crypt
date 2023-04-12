from enum import Enum
import pygame
from models import *


class GameState(Enum):
  STARTUP = 0
  DRAWING = 1
  INPLAY = 2
  DONEPLAY = 3
  WIN = 4
  LOSE = 5
  ENDED = 6


class GameEngine:
  player = None
  enemy = None
  state = None
  
  result = None

  gameStateFromBlockchain = None
  
  def __init__(self, playerDeck, enemyDeck, 
               playerName, enemyName, 
               playerHealth=100, enemyHealth=100, 
               playerStrength=0, enemyStrength=0, 
               playerIntelligence=0, enemyIntelligence=0, 
               playerDexterity=0, enemyDexterity=0, playerImagePath=None, enemyImagePath=None, playerToken="a"*64, enemyID=0):
    
    self.player = Player(playerName, playerDeck, playerHealth, playerStrength, playerIntelligence, playerDexterity, playerImagePath, playerToken)
    self.enemy = Enemy(enemyName, enemyDeck, enemyHealth, enemyStrength, enemyIntelligence, enemyDexterity, enemyImagePath, enemyID)
    self.state = GameState.STARTUP

  def play(self, key):
    if key == None: 
      return
     
    if key == pygame.K_d and self.state == GameState.STARTUP:
      self.state = GameState.DRAWING
      self.player.draw()
      self.enemy.draw()
      return

    if self.state == GameState.DRAWING:
      if key == pygame.K_1:
        self.player.playCard(0)
      elif key == pygame.K_2:
        self.player.playCard(1)
      elif key == pygame.K_3:
        self.player.playCard(2)
      elif key == pygame.K_4:
        self.player.playCard(3) 
      elif key == pygame.K_5:
        self.player.playCard(4)
      elif key == pygame.K_RETURN:
        if (self.player.play[2] != None and self.player.play[1] != None and self.player.play[0] != None):
          self.state = GameState.INPLAY
          # _ = self.player.submitTurnToBlockchain(self.enemy)
          self.enemy.playCard()
          return

