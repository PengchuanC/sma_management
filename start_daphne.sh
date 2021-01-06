
echo start backend server

nohup daphne -p 5000 sma_management.asgi:application > daphne.log &
nohup python3 manage.py qcluster > django_q.log &