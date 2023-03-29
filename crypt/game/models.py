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
  
  def __init__(self, type, value, imagePath):
    self.type = type
    self.value = value
    self.image = pygame.image.load(imagePath)
    self.image = pygame.transform.scale(self.image, (int(238*0.6), int(332*0.6)))


class Deck:
  cards = None
  
  def __init__(self, cards):
    self.cards = cards
    # for type in Types:
    #   for value in range(1,14):
    #     self.cards.append(Card(type, value))
        
  def shuffle(self):
    random.shuffle(self.cards)
    
  def deal(self):
    return self.cards.pop()

  def length(self):
    return len(self.cards)


class Player:
  hand = None
  play = None
  name = None
  image = None
  deck = None
  discard = Deck([])
  health = 100

  strength = 0
  intelligence = 0
  dexterity = 0

  def __init__(self, name, deck, health=100, strength=0, intelligence=0, dexterity=0, imagePath=None):
    self.hand = []
    self.play = [None] * 3
    self.name = name
    self.deck = deck
    self.health = health
    self.image = pygame.image.load(imagePath)
    self.image = pygame.transform.scale(self.image, (int(238*0.8), int(332*0.8)))


    self.strength = strength
    self.intelligence = intelligence
    self.dexterity = dexterity
    
  def draw(self):
    if (self.deck.length() == 0):
      self.deck = Deck(self.discard.cards)
      self.discard = Deck([])
      self.deck.shuffle()
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    
  def playCard(self, cardIndex):
    if (self.hand[cardIndex] == 0):
      self.hand[cardIndex] = self.play[0]
      self.play[0] = None
      return
    elif (self.hand[cardIndex] == 1):
      self.hand[cardIndex] = self.play[1]
      self.play[1] = None
      return
    elif (self.hand[cardIndex] == 2):
      self.hand[cardIndex] = self.play[2]
      self.play[2] = None
      return
    

    if (self.play[0] == None):
      self.play[0] = self.hand[cardIndex]
      self.hand[cardIndex] = 0
    elif (self.play[1] == None):
      self.play[1] = self.hand[cardIndex]
      self.hand[cardIndex] = 1
    elif (self.play[2] == None):
      self.play[2] = self.hand[cardIndex]
      self.hand[cardIndex] = 2
  
  def action(self):
    '''TODO: Implement action logic'''
    self.discard.cards.append(self.play[0])
    self.discard.cards.append(self.play[1])
    self.discard.cards.append(self.play[2])

    self.play = [None] * 3
    for i in range(5):
      if (self.hand[i] != 0 and self.hand[i] != 1 and self.hand[i] != 2):
        self.discard.cards.append(self.hand[i])
    self.hand.clear()
      
  

class Enemy:
  hand = None
  play = [None] * 3
  name = None
  image = None
  deck = None
  discard = Deck([])
  health = 100

  def __init__(self, name, deck, health=100, strength=0, intelligence=0, dexterity=0, imagePath=None ):
    self.hand = []
    self.name = name
    self.deck = deck
    self.health = health
    self.image  = pygame.image.load(imagePath)
    self.image = pygame.transform.scale(self.image, (int(238*0.8), int(332*0.8)))

    self.strength = strength
    self.intelligence = intelligence
    self.dexterity = dexterity
    
  def draw(self):
    if (self.deck.length() == 0):
      self.deck = Deck(self.discard.cards)
      self.discard = Deck([])
      self.deck.shuffle()
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
    self.hand.append(self.deck.deal())
  
  def playCard(self):
    self.play[0] = self.hand[0]
    self.hand[0] = 0

    self.play[1] = self.hand[1]
    self.hand[1] = 1

    self.play[2] = self.hand[2]
    self.hand[2] = 2

  def action(self):
    '''TODO: Implement action logic'''
    self.discard.cards.append(self.play[0])
    self.discard.cards.append(self.play[1])
    self.discard.cards.append(self.play[2])

    self.play = [None] * 3
    for i in range(5):
      if (self.hand[i] != 0 and self.hand[i] != 1 and self.hand[i] != 2):
        self.discard.cards.append(self.hand[i])
    self.hand.clear()