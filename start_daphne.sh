
echo start backend server

nohup daphne -p 8000 sma_management.asgi:application > daphne.log &