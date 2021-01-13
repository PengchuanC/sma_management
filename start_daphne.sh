
echo start backend server

ps aux|grep daphne|grep -v grep|cut -c 9-15|xargs kill -9
ps aux|grep qcluster|grep -v grep|cut -c 9-15|xargs kill -9

sleep 3s

nohup daphne -p 5000 sma_management.asgi:application > daphne.log &
nohup /usr/local/python3/bin/python3 manage.py qcluster > django_q.log &
