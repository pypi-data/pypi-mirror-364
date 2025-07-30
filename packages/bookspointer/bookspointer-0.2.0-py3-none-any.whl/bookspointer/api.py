# Custom imports
from bookspointer.server import BookAPI, TokenAPI

# External imports
from rich import print
import requests

# Standard imports
import json

book_api = BookAPI()
token_api = TokenAPI()


class BookspointerAPI:
    def __init__(self, token):
        self.token = token
        self.url = 'https://api.bookspointer.com/admin/create-book'
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-BD,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Origin': 'https://bookspointer.com',
            'Referer': 'https://bookspointer.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'authorization': f'Bearer {self.token}',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def post_book(self, book):
        if book['category'] == 'অসম্পূর্ণ বই':
            series = 'অসম্পূর্ণ বই'
        else:
            series = ''

        data_dict = {
            "title": book['title'],
            "category": {
                "id": book['category_id'],
            },
            "author": {
                "id": book['author_id'],
            },
            "content": book['content'],
            "tags": [],
            "seriesName": series,
        }

        files = {
            'data': (None, json.dumps(data_dict), 'application/json')
        }

        response = requests.post(self.url, headers=self.headers, files=files)
        book.pop('content')
        print(book)
        try:
            book_id = response.json()['last_book']['id']
            message = f"Book created with ID: {book_id}"
            update_book = book_api.update(book['book_id'], {'is_posted': True})
        except KeyError:
            message = response.json()['message']
            update_book = book_api.update(book['book_id'], {'is_posted': True})
        except Exception as e:
            message = f"Failed to post book {book['title']} : {e}"

        print("Bookspointer Response:", message)
