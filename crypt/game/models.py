from enum import Enum
import pygame
import random
import os
import sys
import io
from urllib.request import urlopen
from algosdk.v2client.algod import AlgodClient
import algokit_utils
from beaker import sandbox
# import gameplay.py from the chain_interaction where crypt is the parent directory of this directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from chain_interaction import gameplay, enemy_generation


class Types(Enum):
  ATTACK = 0
  DEFENSE = 1
  DODGE = 2
class Values(Enum):
  STRENGTH = 0
  INTELLIGENCE = 1
  DEXTERITY = 2

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

  physDamage = 0
  magDamage = 0
  physDefense = 0
  magDefense = 0

  damage = 0

  token = None
  client = None

  address = None

  def __init__(self, name, deck, health=100, strength=0, intelligence=0, dexterity=0, imagePath=None, playerToken="a"*64):
    self.hand = []
    self.play = [None] * 3
    self.name = name
    self.deck = deck
    self.deck.shuffle()
    self.health = health
    self.image = pygame.image.load(imagePath)
    self.image = pygame.transform.scale(self.image, (int(238*0.8), int(332*0.8)))
    self.token = playerToken
    self.client = sandbox.get_algod_client()


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
  
  def damageReduce(self, cardRemoved):
    if (cardRemoved.type == Types.ATTACK):
      if (cardRemoved.value == Values.STRENGTH):
        self.physDamage -= self.strength
      elif (cardRemoved.value == Values.INTELLIGENCE):
        self.magDamage -= self.intelligence
    elif (cardRemoved.type == Types.DEFENSE):
      if (cardRemoved.value == Values.STRENGTH):
        self.physDefense -= self.strength
      elif (cardRemoved.value == Values.INTELLIGENCE):
        self.magDefense -= self.intelligence
      else:
        self.physDefense -= self.dexterity//2
        self.magDefense -= self.dexterity//2
  
  def damageIncrease(self, cardAdded):
    if (cardAdded.type == Types.ATTACK):
      if (cardAdded.value == Values.STRENGTH):
        self.physDamage += self.strength
      elif (cardAdded.value == Values.INTELLIGENCE):
        self.magDamage += self.intelligence
    elif (cardAdded.type == Types.DEFENSE):
      if (cardAdded.value == Values.STRENGTH):
        self.physDefense += self.strength
      elif (cardAdded.value == Values.INTELLIGENCE):
        self.magDefense += self.intelligence
    else:
        self.physDefense += self.dexterity//2
        self.magDefense += self.dexterity//2

  def playCard(self, cardIndex):
    if (self.hand[cardIndex] == 0):
      self.hand[cardIndex] = self.play[0]
      self.play[0] = None
      self.damageReduce(self.hand[cardIndex])
      return
    elif (self.hand[cardIndex] == 1):
      self.hand[cardIndex] = self.play[1]
      self.play[1] = None
      self.damageReduce(self.hand[cardIndex])
      return
    elif (self.hand[cardIndex] == 2):
      self.hand[cardIndex] = self.play[2]
      self.play[2] = None
      self.damageReduce(self.hand[cardIndex])
      return
    

    if (self.play[0] == None):
      self.play[0] = self.hand[cardIndex]
      self.hand[cardIndex] = 0
      self.damageIncrease(self.play[0])
    elif (self.play[1] == None):
      self.play[1] = self.hand[cardIndex]
      self.hand[cardIndex] = 1
      self.damageIncrease(self.play[1])
    elif (self.play[2] == None):
      self.play[2] = self.hand[cardIndex]
      self.hand[cardIndex] = 2
      self.damageIncrease(self.play[2])
  
  def getTypeAndValue(self, card):
    if (card == None):
      return "None", "None"
    if (card.type == Types.ATTACK):
      if (card.value == Values.STRENGTH):
        return "ATTACK", "STRENGTH"
      elif (card.value == Values.INTELLIGENCE):
        return "ATTACK", "INTELLIGENCE"
    elif (card.type == Types.DEFENSE):
      if (card.value == Values.STRENGTH):
        return "DEFENSE", "STRENGTH"
      elif (card.value == Values.INTELLIGENCE):
        return "DEFENSE", "INTELLIGENCE"
    elif (card.type == Types.DODGE):
      return "DODGE", "DEXTERITY"

  def action(self, enemy):
    self.discard.cards.append(self.play[0])
    self.discard.cards.append(self.play[1])
    self.discard.cards.append(self.play[2])

    self.play = [None] * 3
    for i in range(5):
      if (self.hand[i] != 0 and self.hand[i] != 1 and self.hand[i] != 2):
        self.discard.cards.append(self.hand[i])
    self.hand.clear()

  def submitTurnToBlockchain(self, enemy):
    card0Type, card0Value = self.getTypeAndValue(self.play[0])
    card1Type, card1Value = self.getTypeAndValue(self.play[1])
    card2Type, card2Value = self.getTypeAndValue(self.play[2])

    gameState = gameplay.submit_turn(self.client, enemy.enemyID, self.name,
                                                  [[card0Type, card0Value], [card1Type, card1Value], [card2Type, card2Value]])
    return gameState
  
  def resetDamage(self):
    self.physDamage = 0
    self.magDamage = 0
    self.physDefense = 0
    self.magDefense = 0
    self.damage = 0
      
  

class Enemy:
  hand = None
  play = [None] * 3
  name = None
  image = None
  deck = None
  discard = Deck([])
  health = 100

  physDamage = 0
  magDamage = 0
  physDefense = 0
  magDefense = 0

  damage = 0

  enemyID = None

  cardsToPlay = None

  def __init__(self, name, deck, health=100, strength=0, intelligence=0, dexterity=0, imagePath=None, enemyID=None):
    self.hand = []
    self.name = name
    self.deck = deck
    self.deck.shuffle()
    self.health = health
    self.image  = pygame.image.load(imagePath)
    self.image = pygame.transform.scale(self.image, (int(238*0.8), int(332*0.8)))

    self.strength = strength
    self.intelligence = intelligence
    self.dexterity = dexterity

<<<<<<< HEAD
    # self.enemyID = enemy_generation.create_contract("Archmage Zanthorius", 
    #             "Introducing Archmage Zanthorius, master of the arcane and keeper of the eternal flame. \
    #              His powerful spells and unmatched intellect make him a formidable opponent. \
    #              Defeat him and unravel the secrets of the ancient tomes that he guards with his life.", 
    #              "Strength: 9, Intelligence: 34, Dexterity: 14", 
    #              "https://gateway.pinata.cloud/ipfs/QmYyx1aetc2mXU8eYcokZDLy1R1yW51LG5rELYjjx3gKbn?_gl=1*kcxbq9*rs_ga*NTJjNDhmOTItYTEyNy00MzAzLWFmNjItODNkZjExY2FlYzVm*rs_ga_5RMPXG14TE*MTY4MTMxNDY3NS4xLjEuMTY4MTMxNDk2Ni4yMC4wLjA.")
=======
    self.enemyID = enemy_generation.create_contract("Archmage Zanthorius", 
                "Introducing Archmage Zanthorius, master of the arcane and keeper of the eternal flame. \
                 His powerful spells and unmatched intellect make him a formidable opponent. \
                 Defeat him and unravel the secrets of the ancient tomes that he guards with his life.", 
                 "Strength: 9, Intelligence: 34, Dexterity: 14", 
                 "https://gateway.pinata.cloud/ipfs/QmYyx1aetc2mXU8eYcokZDLy1R1yW51LG5rELYjjx3gKbn?_gl=1*kcxbq9*rs_ga*NTJjNDhmOTItYTEyNy00MzAzLWFmNjItODNkZjExY2FlYzVm*rs_ga_5RMPXG14TE*MTY4MTMxNDY3NS4xLjEuMTY4MTMxNDk2Ni4yMC4wLjA.")
    
>>>>>>> 1e92abd0a6242e32df0368221bd2301ed50c2b2a

    self.enemyID = enemyID
    
    self.cardsToPlay = [Card(Types.ATTACK,Values.INTELLIGENCE,r"images/Arcane Nova.png"),
                        Card(Types.DODGE,Values.DEXTERITY,r"images/Ethereal Dodge.png"),
                        Card(Types.DEFENSE,Values.INTELLIGENCE,r"images/Elemental Aegis.png")]

    
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
  
  def getCardFromChainInfo(self, cardInfo):
    if (cardInfo[0] == "ATTACK"):
      if (cardInfo[1] == "STRENGTH"):
        return Card(Types.ATTACK, Values.STRENGTH, "images/SWORDATTACKSTR.png.png")
      elif (cardInfo[1] == "INTELLIGENCE"):
        return Card(Types.ATTACK, Values.INTELLIGENCE, "images/LIGHTNINGATTACKINTELL.png")
    elif (cardInfo[0] == "DEFENSE"):
      if (cardInfo[1] == "STRENGTH"):
        return Card(Types.DEFENSE, Values.STRENGTH, "images/SHIELDDEFENSESTR.png")
      elif (cardInfo[1] == "INTELLIGENCE"):
        return Card(Types.DEFENSE, Values.INTELLIGENCE, "images/ELIXIRDEFENSEINTELL.png")
    elif (cardInfo[0] == "DODGE"):
      return Card(Types.DODGE, Values.DEXTERITY, "images/DODGE.png")
    else:
      return None
    
  def playCard(self, enemyTurn=None, gameState=None):
    drawnCards = random.sample(range(0,5),3)
    played = random.sample(range(0,3),3)
    # self.play[0] = self.getCardFromChainInfo(enemyTurn[0])
    self.play[0] = self.cardsToPlay[played[0]]
    self.hand[drawnCards[0]] = 0

    # self.play[1] = self.getCardFromChainInfo(enemyTurn[1])
    self.play[1] = self.cardsToPlay[played[1]]
    self.hand[drawnCards[1]] = 1

    # self.play[2] = self.getCardFromChainInfo(enemyTurn[2])
    self.play[2] = self.cardsToPlay[played[2]]
    self.hand[drawnCards[2]] = 2

    for card in self.play:
      if (card.type == Types.ATTACK):
        if (card.value == Values.STRENGTH):
          self.physDamage += self.strength
        elif (card.value == Values.INTELLIGENCE):
          self.magDamage += self.intelligence
      elif (card.type == Types.DEFENSE):
        if (card.value == Values.STRENGTH):
          self.physDefense += self.strength
        elif (card.value == Values.INTELLIGENCE):
          self.magDefense += self.intelligence
      else:
        self.physDefense += self.dexterity//2
        self.magDefense += self.dexterity//2

  def action(self):
    

    self.discard.cards.append(self.play[0])
    self.discard.cards.append(self.play[1])
    self.discard.cards.append(self.play[2])
    


    self.play = [None] * 3
    for i in range(5):
      if (self.hand[i] != 0 and self.hand[i] != 1 and self.hand[i] != 2):
        self.discard.cards.append(self.hand[i])
    self.hand.clear()
  
  def resetDamage(self):
    self.physDamage = 0
    self.magDamage = 0
    self.physDefense = 0
    self.magDefense = 0
    self.damage = 0
  
  def replenishDeck(self):
    for i in self.discard.cards:
      self.deck.cards.append(i)
    self.discard = Deck([])
    self.deck.shuffle()