import pika
from mongoengine import connect, Document, StringField, BooleanField
from faker import Faker
import json

# Підключення до бази даних MongoDB
connect('rabbitmq_demo', host='localhost', port=27017)



# Модель для контакту
class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(default=False)

# Задаємо параметри підключення до RabbitMQ
rabbitmq_params = pika.ConnectionParameters(host='localhost', port=5672)
connection = pika.BlockingConnection(rabbitmq_params)
channel = connection.channel()

# Задаємо назву черги
queue_name = 'contacts_queue'
channel.queue_declare(queue=queue_name)

# Генеруємо та записуємо фейкові контакти у базу даних та відправляємо їх у чергу
fake = Faker()
for _ in range(5):  # Генеруємо 5 контактів для прикладу
    contact = Contact(
        fullname=fake.name(),
        email=fake.email()
    )
    contact.save()

    # Відправляємо ID контакту у чергу
    message = {'contact_id': str(contact.id)}
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message))
    print(f"Contact added to the queue: {contact.fullname}")

# Закриваємо підключення до RabbitMQ
connection.close()
