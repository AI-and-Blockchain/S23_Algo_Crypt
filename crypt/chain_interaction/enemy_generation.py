import openai
import random
import typing
import base64
import os
import json
import ipfshttpclient
import requests
from beaker import sandbox
from algosdk.transaction import PaymentTxn, ApplicationCreateTxn
from algosdk import transaction

from dotenv import load_dotenv
from algosdk.v2client.algod import AlgodClient
from algosdk import mnemonic
from algokit_utils import (
    ApplicationClient,
    get_account,
    get_algod_client
)

load_dotenv(os.path.join(
    os.path.dirname(__file__),
    "../.env"
))

ALGOD_API_ADDR = os.getenv("ALGOD_API_ADDR", "http://localhost:4001")
ALGOD_API_TOKEN = os.getenv("ALGOD_API_TOKEN")
CREATOR_MNEMONIC = os.getenv("CREATOR_MNEMONIC")

# Initialize Algod client
algod_client = AlgodClient(algod_token=ALGOD_API_TOKEN, algod_address=ALGOD_API_ADDR)


#replace YOUR_API_KEY with your api key
openai.api_key = "YOUR_API_KEY"


def generate_enemy() -> typing.Tuple[str, str, str]:
    enemy_categories = ["wizard", "elf", "paladin", "hunter", "dragon", "warlock", "demon", "monster", "treant", 
                        "murloc", "thief", "beast", "priest", "shaman", "warrior", "undead", "orc", "titan"]
    category = random.choice(enemy_categories)

    prompt = f"I am designing a Massively-Multiplayer Online Trading Card Game on the Algorand Blockchain. \
        The game story background is similar to the combination of card games like Hearthstone and Magic: The Gathering. \
        The blockchain hosts a bounty list of AI-generated enemies. Players build a deck of NFT cards to challenge them \
        in a card game to the death. So, for now, I need you to generate an attracting, appropriate, interesting, \
        but short (less than five sentences) description of a unique {category} enemy. It could have a name. Also, there could be many \
        enemies from the same category, so the description should be specific."

    response1 = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    description = response1.choices[0].text.strip()

    prompt_st = f"I am designing a Massively-Multiplayer Online Trading Card Game on the Algorand Blockchain. \
        The game story background is similar to the combination of card games like Hearthstone and Magic: The Gathering. \
        The blockchain hosts a bounty list of AI-generated enemies. Players build a deck of NFT cards to challenge them \
        in a card game to the death.\
        The categories for enemies in this game include wizard, elf, paladin, hunter, dragon, warlock, demon, monster, treant, murloc, thief, and animals\
        Based on the description here: {description};\
        I need you to generate stat block for this enemy: it should include strength, intelligence, \
        and dexterity of this enemy, which will be numbers between 1 and 100. Since there will be a lot of enemies \
        in my card game, so the stat block for each enemy should be appropriate and reasonable. For example, \
        wizard can have higher intelligence because he knows magic; as a result, a young wizard could have 7, 14, 8 \
        while an elder wizard can have 10, 30, 12. Similarly, paladin, and hunter may have higher strength. \
        Also, demon and dragon are powerful, so they can have both high strength and intelligence, like: 28, 32, 19 or 40 55 39. \
        To be noticed that these numbers can not be very close to 100 because 100 means unbeatable. Just give me these three numbers."

    response2 = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_st,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    stats = response2.choices[0].text.strip()
    image_prompt = f"Based on the description here: {description}; \
        I will need an appropriate, beautiful, and attractive image \
        in a Pixel Art style with intriguing background\
        to represent this enemy, so I need you to generate an image generation prompt \
        for this enemy that can be used in dall e. \
        This image will be used as a NFT in the card game later, so it should have high quality. "

    response3 = openai.Completion.create(
        engine="text-davinci-003",
        prompt=image_prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )

    dalle_prompt = response3.choices[0].text.strip()

    response = openai.Image.create(
        prompt=dalle_prompt,
        n=1,
        size="256x256",
    )

    image = response["data"][0]["url"]

    return (description, stats, image)


def generate_enemies(n):
    enemies = []

    for i in range(n):
        enemy = generate_enemy()
        enemies.append(enemy)

    return enemies


def ipfs_upload(image_url: str) -> str:
    """Upload image at given url to IPFS.

    Args:
        image_url (str): url of image to upload

    Returns:
        str: IPFS uri of uploaded image
    """
    # Connect to a local IPFS node
    client = ipfshttpclient.connect()

    # Download the image data from the URL
    response = requests.get(image_url)
    image_data = response.content

    # Add the image data to IPFS
    result = client.add_bytes(image_data)

    # Return the IPFS uri
    ipfs_uri = f"ipfs://{result}"
    return ipfs_uri


def create_contract(name: str, description: str, stats: str, image: str) -> str:
    """Create a contract for an enemy.

    Args:
        name (str): name of enemy
        description (str): description of enemy
        stats (str): stats of enemy
        image (str): ipfs uri of image of enemy

    Returns:
        str: address of contract
    """
    creator_account = mnemonic.to_private_key(CREATOR_MNEMONIC)
    creator_addr = mnemonic.to_public_key(CREATOR_MNEMONIC)

    app_client = ApplicationClient(
        algod_client=algod_client,
        app_spec=os.path.join(
            os.path.dirname(__file__),
            "../blockchain/smart_contracts/artifacts/Enemy Contract/application.json"
        ),
        sender=creator_addr
    )

    app_client.create(creator_account)

    app_client.call(
        "update",
        name=name,
        description=description,
        stats=stats,
        image_uri=image,
        signer=creator_account
    )

    return app_client.app_address


def main(num_enemies: int = 10):
    #enemies = generate_enemies(num_enemies)
    
    #for test 
    enemies = [ ("Archmage Zanthorius", 
                "Introducing Archmage Zanthorius, master of the arcane and keeper of the eternal flame. \
                 His powerful spells and unmatched intellect make him a formidable opponent. \
                 Defeat him and unravel the secrets of the ancient tomes that he guards with his life.", 
                 "Strength: 9, Intelligence: 34, Dexterity: 14", 
                 "https://gateway.pinata.cloud/ipfs/QmYyx1aetc2mXU8eYcokZDLy1R1yW51LG5rELYjjx3gKbn?_gl=1*kcxbq9*rs_ga*NTJjNDhmOTItYTEyNy00MzAzLWFmNjItODNkZjExY2FlYzVm*rs_ga_5RMPXG14TE*MTY4MTMxNDY3NS4xLjEuMTY4MTMxNDk2Ni4yMC4wLjA.") ]

 

    for enemy in enemies:
        name, description, stats, image = enemy
        #image = ipfs_upload(image)
        add = create_contract(name, description, stats, image)
        print(add)


if __name__ == "__main__":
    main()
