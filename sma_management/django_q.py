from django_q.brokers import Broker


class CustomBroker(Broker):
    def info(self):
        return 'My Custom Broker'
