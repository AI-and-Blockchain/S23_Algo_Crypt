from enum import Enum
import pygame
import random

class Types(Enum):
  ATTACK = 0
  DEFENSE = 1
  DODGE = 2

class Card:
  type = None
  value = None
  image = None
  
  def __init__(self, type, value):
    self.type = type
    self.value = value
    self.image = pygame.image.load('images/BACK.png')


class Deck:
  cards = None
  
  def __init__(self):
    self.cards = []
    for suit in Suits:
      for value in range(1,14):
        self.cards.append(Card(suit, value))
        
  def shuffle(self):
    random.shuffle(self.cards)
    
  def deal(self):
    return self.cards.pop()

  def length(self):
    return len(self.cards)


class Player:
  hand = None
  flipKey = None
  snapKey = None
  name = None

  def __init__(self, name, flipKey, snapKey):
    self.hand = []
    self.flipKey = flipKey
    self.snapKey = snapKey
    self.name = name
    
  def draw(self, deck):
    self.hand.append(deck.deal())
    
  def play(self):
    return self.hand.pop(0)

class Enemy:
  hand = None
  flipKey = None
  snapKey = None
  name = None

  def __init__(self, name, flipKey, snapKey):
    self.hand = []
    self.flipKey = flipKey
    self.snapKey = snapKey
    self.name = name
    
  def draw(self, deck):
    self.hand.append(deck.deal())
    
  def play(self):
    return self.hand.pop(0)