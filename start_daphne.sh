
echo start backend server

ps aux|grep 5000|grep -v grep|cut -c 9-15|xargs kill -9
ps aux|grep qcluster|grep -v grep|cut -c 9-15|xargs kill -9
ps aux|grep stock_async|grep -v grep|cut -c 9-15|xargs kill -9

sleep 3s

nohup daphne -p 5000 sma_management.asgi:application > daphne.log &
nohup /usr/local/python3/bin/python3 manage.py qcluster > django_q.log &
nohup /usr/local/python3/bin/python3 -m crawl.stock_async > stock_price.log &
