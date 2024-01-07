from mongoengine import connect, Document, StringField, DateTimeField, ReferenceField, ListField
import json

# Підключення до бази даних
connect(db='hw', host='localhost', port=27017)


# Модель для колекції authors
class Author(Document):
    fullname = StringField(required=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()


# Модель для колекції quotes
class Quote(Document):
    tags = ListField(StringField())
    author = ReferenceField(Author)
    quote = StringField()


# Завантаження даних з файлу authors.json
with open('authors.json', 'r') as file:
    authors_data = json.load(file)

# Завантаження даних з файлу quotes.json
with open('quotes.json', 'r') as file:
    quotes_data = json.load(file)

Author.objects().delete()
Quote.objects().delete()

# Заповнення колекції authors
for author_info in authors_data:
    author = Author(**author_info)
    author.save()
    print(f"Added author: {author.fullname}")

# Заповнення колекції quotes з використанням ReferenceField для авторів
for quote_info in quotes_data:
    author = Author.objects(fullname=quote_info['author']).first()
    quote_info['author'] = author
    quote = Quote(**quote_info)
    quote.save()
    print(f"Added quote by {quote.author.fullname}: {quote.quote}")

# Скрипт для пошуку цитат за тегом, за ім'ям автора або набором тегів
while True:
    command = input("Enter command (name, tag, tags, exit): ").strip().lower()

    if command.startswith("name:"):
        author_name = command.split(":")[1].strip()
        author = Author.objects(fullname__icontains=author_name).first()
        if author:
            quotes = Quote.objects(author=author)
            for quote in quotes:
                print(quote.quote)
        else:
            print("Author not found.")

    elif command.startswith("tag:"):
        tag = command.split(":")[1].strip()
        quotes = Quote.objects(tags=tag)
        for quote in quotes:
            print(quote.quote)

    elif command.startswith("tags:"):
        tags = command.split(":")[1].strip().split(',')
        quotes = Quote.objects(tags__in=tags)
        for quote in quotes:
            print(quote.quote)

    elif command == "exit":
        break

    else:
        print("Invalid command.")
