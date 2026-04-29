<!-- @format -->

## Start Docker

docker-compose up --build

## Write data in DataBase

python src/database/populate.py

## Run Server

uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
