# Algo Crypt

A Massively-Multiplayer Online Trading Card Game on the Algorand Blockchain

# Overview

The blockchain hosts a bounty list of AI-generated enemies. Players build a deck of NFT cards to challenge them in a card game to the death. Players browse the list and select enemies to hunt, with the first player to defeat an enemy rewarded with an NFT representation of the defeated enemy as well as a random selection of cards from that enemy’s deck. Players can trade enemy and card NFTs on an associated marketplace, collecting cards to use in PvE or PvP battles. Cards and enemies will have associated rarities and varying values.

The AI component includes use of GPT-3 to generate stat blocks for enemies (strength, intelligence, dexterity) from a thematic prompt. Then, the stat block and theme are passed to DallE to generate an image to represent that stat block. 

The blockchain component runs on Algorand. All cards and enemies are represented as NFTs using Algorand standard assets. The blockchain also validates games and winnings as a ledger of games and actions. The card and enemy marketplace will run on this blockchain as well using the CRPT asset. The use of blockchain also allows for validation of physical games with the introduction of a smart playmat and physical cards in a future project.

# Instructions

Install game
Run
How to play
etc.

# Technology Stack

## Technologies
## Frameworks
## Library dependencies

# Project Structure

```
- root
    - algo_crypt
        - game
        - contracts
        - api
        - marketplace
        - asset_generation
```

# System Design

## Overview

Overview of system

## Gameplay

Here goes information about gameplay and how to play the game.

## NFT Minting and Distribution

Here goes information about minting and distributing the card and enemy NFTs. It includes at what stage it happens and how it's accomplished.

## Enemy Generation

Here is information about the process for generating enemiess statblocks and images.

## NFT Marketplace

Information about the NFT marketplace for cards and defeated enemies (including rarities, value, etc).

# Future Projects

Talk about physical playmat, other future projects

# Developers

Name, Institution (RPI), email
