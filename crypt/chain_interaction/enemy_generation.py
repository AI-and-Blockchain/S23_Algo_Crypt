import openai
import random
import typing
import base64
import os
import json
import ipfshttpclient
import requests
from algokit_utils import get_algod_client, get_account
from beaker import sandbox
from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import PaymentTxn, ApplicationCreateTxn
from algosdk import mnemonic, transaction

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
    algod_client = get_algod_client()

    CREATOR_MNEMONIC = os.environ["CREATOR_MNEMONIC"]
    creator_private_key = mnemonic.to_private_key(CREATOR_MNEMONIC)
    creator_address = mnemonic.to_public_key(CREATOR_MNEMONIC)

    # Set up the contract
    # Teal script
    enemy_contract = '''
        #pragma version 2
        txn CloseRemainderTo
        addr <CREATOR_ADDRESS>
        ==
        txn Receiver
        addr <CREATOR_ADDRESS>
        ==
        &&
        txn AssetCloseTo
        addr <CREATOR_ADDRESS>
        ==
        &&
    '''
    
    # Compile the contract
    compile_response = algod_client.compile(enemy_contract)
    contract_address = compile_response['hash']
    contract_bytes = base64.b64decode(compile_response['result'])

    # Fund the contract
    params = algod_client.suggested_params()
    txn = PaymentTxn(creator_address, params, contract_address, 100000, note=base64.b64encode(contract_bytes))
    signed_txn = txn.sign(creator_private_key)
    txn_id = algod_client.send_transaction(signed_txn)
    sandbox.wait_for_confirmation(algod_client, txn_id)

    # Create contract deployment transaction
    app_args = [name, description, stats, image]
    txn = ApplicationCreateTxn(creator_address, params, transaction.OnCompletion.NoOpOC, contract_bytes, app_args)
    signed_txn = txn.sign(creator_private_key)
    txn_id = algod_client.send_transaction(signed_txn)
    sandbox.wait_for_confirmation(algod_client, txn_id)

    return contract_address



def main(num_enemies: int = 10):
    enemies = generate_enemies(num_enemies)

    for enemy in enemies:
        description, stats, image = enemy
        image = ipfs_upload(image)
        create_contract(description, stats, image)


if __name__ == "__main__":
    main()
