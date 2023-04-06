pip install -r requirements.txt
algokit localnet start
algokit localnet status
cd ./crypt/blockchain
python -m smart_contracts all
cd ../..
cd ./crypt/api
uvicorn main:app --reload
cd ../..
cd ./frontend
npm start
