pip install -r requirements.txt
algokit localnet start
algokit localnet status
cd ./crypt/blockchain
python -m smart_contracts all
cd ../..
<<<<<<< HEAD
cd ./crypt/api
uvicorn main:app --reload
cd ../..
cd ./frontend
npm start
cd ../game
python main.py 100 75 25 9 10 34 15 14  Player aaa 1 'Archmage Zanthorius' 'images/pala.png' 'images/Archmage Zanthorius.png' 2
=======
python starting_cards.py
cd ./crypt/game
python main.py 100 75 25 9 10 34 15 14  Player aaa 1 'Archmage Zanthorius' 'images/pala.png' 'images/Archmage Zanthorius.png' 52.2
>>>>>>> 1e92abd0a6242e32df0368221bd2301ed50c2b2a
