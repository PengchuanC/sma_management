
echo start backend server

nohup daphne -p 5000 sma_management.asgi:application > daphne.log &