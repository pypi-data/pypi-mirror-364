# External imports
from dotenv import load_dotenv
from rich import print
import requests

# Standard imports
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


class BaseAPI:
    """
    BaseAPI provides basic HTTP methods (_get, _post, _patch, _delete) for interacting with a RESTful API.
    All other API classes inherit from this to perform CRUD operations.
    """

    def __init__(self, base_url=BASE_URL):
        """
        Initialize the API with a base URL.
        :param base_url: The root URL for the API endpoints.
        """
        self.base_url = base_url

    def _get(self, endpoint):
        """
        Send a GET request to the specified endpoint.
        :param endpoint: API endpoint (string)
        :return: Response object
        """
        return requests.get(f"{self.base_url}{endpoint}")

    def _post(self, endpoint, data):
        """
        Send a POST request to the specified endpoint with JSON data.
        :param endpoint: API endpoint (string)
        :param data: Data to send (dict)
        :return: Response object
        """
        return requests.post(f"{self.base_url}{endpoint}", json=data)

    def _patch(self, endpoint, data):
        """
        Send a PATCH request to the specified endpoint with JSON data.
        :param endpoint: API endpoint (string)
        :param data: Data to update (dict)
        :return: Response object
        """
        return requests.patch(f"{self.base_url}{endpoint}", json=data)

    def _delete(self, endpoint, headers=None):
        """
        Send a DELETE request to the specified endpoint.
        :param endpoint: API endpoint (string)
        :param headers: Optional headers (dict)
        :return: JSON response or error message
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError:
                return {"status": "success", "message": "Deleted", "status_code": response.status_code}
        except requests.RequestException as e:
            print(f"[red]DELETE request failed for {url}: {e}[/red]")
            return {"status": "error", "message": str(e)}


class BookAPI(BaseAPI):
    """
    BookAPI provides methods to create, update, delete, and retrieve books via the API.
    Inherits from BaseAPI.
    """

    def create(self, book_data: dict):
        """
        Create a new book entry in the API.
        :param book_data: Dictionary containing book details.
        :return: Book ID if successful, or error message.
        """
        data = {
            "book_id": book_data['book_id'],
            "title": book_data['title'],
            "author": book_data['author'],
            "author_id": book_data['author_id'],
            "category": ','.join(book_data['category']),
            "category_id": book_data['category_id'],
            "book_link": book_data['url'],
            "content": book_data['content'],
        }
        response = self._post("books/", data)
        try:
            resp_json = response.json()
        except Exception:
            resp_json = {}
        if hasattr(response, 'status_code') and response.status_code == 201 and resp_json.get('book_id'):
            print(
                f"Book created successfully. Title: {data.get('title')}, ID: {resp_json.get('book_id')}")
            return resp_json.get('book_id', '')
        else:
            error_msg = resp_json.get('message', response.text if hasattr(
                response, 'text') else 'Unknown error')
            print(f"Failed to create book: {error_msg}")
            return {"success": False, "message": error_msg}

    def update(self, book_id: int, updated_data: dict):
        """
        Update an existing book entry.
        :param book_id: ID of the book to update.
        :param updated_data: Dictionary of fields to update.
        :return: Success or error message.
        """
        response = self._patch(f"books/{book_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update book {book_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Book {book_id} updated successfully.")
        return {"success": True, "message": f"Book {book_id} updated."}

    def delete(self, book_id):
        """
        Delete a book entry by its ID.
        :param book_id: ID of the book to delete.
        :return: Success or error message.
        """
        response = self._delete(f"books/{book_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete book {book_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Book {book_id} deleted successfully.")
        return {"success": True, "message": f"Book {book_id} deleted."}

    def get(self, book_id=None):
        """
        Retrieve a book by ID, or all books if no ID is provided.
        :param book_id: (Optional) ID of the book.
        :return: Book data or list of books.
        """
        if book_id:
            data = self._get(f"books/{book_id}/").json()
            if isinstance(data, dict) and "content" in data:
                data.pop("content")
            return data
        data = self._get("books/").json()
        if isinstance(data, list):
            for book in data:
                if "content" in book:
                    book.pop("content")
        return data

    def get_all_books(self, is_posted=False):
        """
        Retrieve all books, optionally filtering by 'is_posted' status.
        :param is_posted: Boolean to filter books.
        :return: List of books.
        """
        response = self._get("books/")
        if response.status_code == 200:
            books = [book for book in response.json(
            ) if book.get('is_posted') == is_posted]
            if len(books) == 0:
                print('All books are up to date')
                return []
            print("📚 All Books:")
            for book in books:
                print(
                    f"ID: {book.get('book_id')}, Title: {book.get('title')}, Author: {book.get('author')}")
        else:
            print(f"❌ Failed to retrieve books: {response.status_code}")
            print("Response:", response.text)
            return []
        return books


class AuthorAPI(BaseAPI):
    """
    AuthorAPI provides methods to create, update, delete, and retrieve authors via the API.
    Inherits from BaseAPI.
    """

    def create(self, author_data):
        """
        Create a new author entry in the API.
        :param author_data: Dictionary containing author details.
        :return: Author ID if successful, or error message.
        """
        author = {
            "author_id": author_data['id'],
            "author_name": author_data['full_name'],
            "author_link": author_data['author_link']
        }
        
        response = self._post("authors/", author)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create author: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Author created successfully. Name: {author.get('author_name')}")
        return {"success": True, "message": f"Author '{author.get('name', author.get('author'))}' created.", "id": obj_id}

    def update(self, author_id, updated_data):
        """
        Update an existing author entry.
        :param author_id: ID of the author to update.
        :param updated_data: Dictionary of fields to update.
        :return: Success or error message.
        """
        response = self._patch(f"authors/{author_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update author {author_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Author updated successfully.")
        return {"success": True, "message": f"Author {author_id} updated."}

    def delete(self, author_id):
        """
        Delete an author entry by its ID.
        :param author_id: ID of the author to delete.
        :return: Success or error message.
        """
        response = self._delete(f"authors/{author_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete author {author_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Author {author_id} deleted successfully.")
        return {"success": True, "message": f"Author {author_id} deleted."}

    def get(self, author_id=None):
        """
        Retrieve an author by ID, or all authors if no ID is provided.
        :param author_id: (Optional) ID of the author.
        :return: Author data or list of authors.
        """
        if author_id:
            return self._get(f"authors/{author_id}/").json()
        return self._get("authors/").json()

    def get_all_authors(self):
        """
        Retrieve all authors from the API.
        :return: List of authors.
        """
        response = self._get("authors/")
        if response.status_code == 200:
            authors = response.json()
            print(f"Authors found: {len(authors)}")
            return authors
        else:
            print(f"❌ Failed to retrieve authors: {response.status_code}")
            print("Response:", response.text)
            return []

    def get_unscraped_authors(self):
        """
        Retrieve all authors from the API that are not marked as scraped.
        :return: List of unscraped authors.
        """
        response = self._get("authors/")
        if response.status_code == 200:
            authors = response.json()
            unscraped = [a for a in authors if a.get('is_scraped') == "no"]
            print(f"Unscraped authors found: {len(unscraped)}")
            return unscraped
        else:
            print(f"❌ Failed to retrieve authors: {response.status_code}")
            print("Response:", response.text)
            return []


class TokenAPI(BaseAPI):
    """
    TokenAPI provides methods to create, update, and delete user tokens via the API.
    Inherits from BaseAPI.
    """

    def create(self, token_data):
        """
        Create a new user token entry in the API.
        :param token_data: Dictionary containing token details.
        :return: Token ID if successful, or error message.
        """
        response = self._post("users/", token_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create token: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Token created successfully for user: {token_data.get('username', token_data.get('user_id'))}")
        return {"success": True, "message": f"Token for user '{token_data.get('username', token_data.get('user_id'))}' created.", "id": obj_id}

    def update(self, user_id, updated_data):
        """
        Update an existing user token entry.
        :param user_id: ID of the user whose token to update.
        :param updated_data: Dictionary of fields to update.
        :return: Success or error message.
        """
        response = self._patch(f"users/{user_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update token for user {user_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Token for user {user_id} updated successfully.")
        return {"success": True, "message": f"Token for user {user_id} updated."}
    
    def get_all_tokens(self):
        """
        Retrieve all user tokens from the API.
        :return: List of user tokens.
        """
        response = self._get("users/")
        
        if response.status_code == 200:
            tokens = [token.get('token') for token in response.json()]
            return tokens
        else:
            print(f"❌ Failed to retrieve tokens: {response.status_code}")
            print("Response:", response.text)
            return []

    def delete(self, user_id):
        """
        Delete a user token entry by its ID.
        :param user_id: ID of the user whose token to delete.
        :return: Success or error message.
        """
        response = self._delete(f"users/{user_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete token for user {user_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Token for user {user_id} deleted successfully.")
        return {"success": True, "message": f"Token for user {user_id} deleted."}

    def get(self, user_id=None):
        """
        Retrieve a user by ID, or all users if no ID is provided.
        :param user_id: (Optional) ID of the user.
        :return: User data or list of users.
        """
        import random
        if user_id:
            return self._get(f"users/{user_id}/").json()
        data = self._get("users/").json()
        if isinstance(data, list):
            random.shuffle(data)
        return data


class CategoryAPI(BaseAPI):
    """
    CategoryAPI provides methods to create, update, and delete categories via the API.
    Inherits from BaseAPI.
    """

    def create(self, category_data):
        """
        Create a new category entry in the API.
        :param category_data: Dictionary containing category details.
        :return: Category ID if successful, or error message.
        """
        response = self._post("categories/", category_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(f"Failed to create category: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        obj_id = None
        try:
            obj_id = response.json().get("id", "")
        except Exception:
            pass
        print(
            f"Category created successfully. Name: {category_data.get('name', category_data.get('category'))}")
        return {"success": True, "message": f"Category '{category_data.get('name', category_data.get('category'))}' created.", "id": obj_id}

    def update(self, category_id, updated_data):
        """
        Update an existing category entry.
        :param category_id: ID of the category to update.
        :param updated_data: Dictionary of fields to update.
        :return: Success or error message.
        """
        response = self._patch(f"categories/{category_id}/", updated_data)
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to update category {category_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Category {category_id} updated successfully.")
        return {"success": True, "message": f"Category {category_id} updated."}

    def delete(self, category_id):
        """
        Delete a category entry by its ID.
        :param category_id: ID of the category to delete.
        :return: Success or error message.
        """
        response = self._delete(f"categories/{category_id}/")
        if isinstance(response, dict) and response.get("status") == "error":
            print(
                f"Failed to delete category {category_id}: {response.get('message')}")
            return {"success": False, "message": response.get("message")}
        print(f"Category {category_id} deleted successfully.")
        return {"success": True, "message": f"Category {category_id} deleted."}

    def get(self, category_id=None):
        """
        Retrieve a category by ID, or all categories if no ID is provided.
        :param category_id: (Optional) ID of the category.
        :return: Category data or list of categories.
        """
        if category_id:
            return self._get(f"categories/{category_id}/").json()
        return self._get("categories/").json()
