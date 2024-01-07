import pika
from mongoengine import connect, disconnect, Document, StringField, BooleanField
import json
from faker import Faker

# Підключення до бази даних MongoDB
connect('rabbitmq_demo', host='localhost', port=27017)

# Модель для контакту
class Contact(Document):
    fullname = StringField(required=True)
    email = StringField(required=True)
    message_sent = BooleanField(default=False)

try:
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

    print('Waiting for messages. To exit press CTRL+C')
    # Очікуємо повідомлення з черги та викликаємо функцію-заглушку
    channel.start_consuming()

except Exception as e:
    print(f"Error during RabbitMQ connection: {e}")

finally:
    # Закриваємо підключення до RabbitMQ
    try:
        connection.close()
    except:
        pass

    # Також, закрийте підключення до MongoDB
    try:
        disconnect(alias='rabbitmq_demo')
    except:
        pass
