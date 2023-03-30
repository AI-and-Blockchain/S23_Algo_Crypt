import openai
import random

#replace YOUR_API_KEY with your api key
openai.api_key = "YOUR_API_KEY"


def generate_enemy():
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
        I will need an appropriate, beautiful, attarcting, and realistic digital painting \
        in the style of Hearthstone with intriguing background\
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


    print(dalle_prompt)
    print()


    response = openai.Image.create(
        prompt = dalle_prompt,
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


enemies = generate_enemies(1)
print(enemies)


