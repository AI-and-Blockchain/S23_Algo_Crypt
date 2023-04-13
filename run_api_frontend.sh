npm install pm2 -g
npm install react-scripts -g
cd ./crypt/api
uvicorn main:app --reload
cd ../..
cd ./frontend
npm ci
pm2 start npm -- start