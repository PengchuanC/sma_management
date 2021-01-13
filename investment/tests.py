from django.test import Client


client = Client()
resp = client.get('/management/api/v1/test/')
print(resp.content_type)
