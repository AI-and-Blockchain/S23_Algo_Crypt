npm install pm2 -g
cd ./crypt/api
uvicorn main:app --reload
cd ../..
cd ./frontend
pm2 start npm -- start