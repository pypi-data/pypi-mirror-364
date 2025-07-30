# External imports
from selectolax.parser import HTMLParser
import importlib.resources
from rich import print
import requests

# Standard imports
import json


class BookScraper:
    """
    BookScraper is responsible for scraping book data from ebanglalibrary.com.
    It provides methods to fetch book lists, details, content, and category IDs.
    """

    def __init__(self, single_page_cate: list):
        """
        Initialize the BookScraper with a list of single-page category IDs.

        Args:
            single_page_cate (list): List of category IDs that are single-page.
        """
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-BD,en-US;q=0.9,en;q=0.8",
            "priority": "u=1, i",
            "referer": "https://www.ebanglalibrary.com/",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        self.cookies = {
            "__gsas": "ID=eeb6a89775d353fc:T=1749577672:RT=1749577672:S=ALNI_MaIBex_3dHulhrGnFupNiyLCvPZsA",
            "cf_clearance": "UDM6zG5aQdnupSDm_pIrI0ahH3Qhf0C4OlzwVW3v9lc-1749711078-1.2.1.1-d6Cn4han6cxVdvXh8d2rCs94t44Ld6FDxpbHkRtKHfqp7kvMLSiNwJkjP_Y__l3tMmK4DA04X6WQG8hAav42mW6h3knRv6Tn_2XUgVAGngGmpizLslySbsm0riaopY33XFSRQ8nafhbavhdijYjzSI3JIbbsj1yywKSkFfloHhS0gPloasy7HFH8CNOlxF.lH7O7AsRJ7X5UMqJrmtk4LrAK4jskS5pp9vcOOIuo.hRqQ5NhlzFZklFpti22RVcmn1t463Z6DM8sAQbrlPObjp9qJYlaZo22uSHjLECc9uXeMy4cf_Xj8qjxPUTbOqpXmDM3qLHnC0563ZpCQHxLZBl2stE1Dr.gOaouTSAC_sw",
            "advanced_ads_visitor": '{"browser_width":1905}'
        }
        self.single_page_cate = single_page_cate

    def get_pages(self, book_id: int) -> list:
        """
        Retrieve all page URLs for a given book by its ID.

        Args:
            book_id (int): The ID of the book.

        Returns:
            list: List of page URLs.
        """
        url = "https://www.ebanglalibrary.com/wp-admin/admin-ajax.php"

        page_number = 1
        querystring = {"action": ["ld30_ajax_pager", "ld30_ajax_pager"], "pager_nonce": "26c3c2da05", "context": "course_content_shortcode",
                       "course_id": book_id, "shortcode_instance[course_id]": book_id, "shortcode_instance[num]": "100"}

        response = requests.get(url, headers=self.headers,
                                cookies=self.cookies, params=querystring)

        data = response.json()['data']['markup']
        html = HTMLParser(data)
        book_urls = [a.attributes.get('href', '')
                     for a in html.css('a.ld-item-name')]
        return book_urls

    def get_html_pages(self, book_url: str) -> list:
        """
        Retrieve all HTML page URLs for a given book URL.

        Args:
            book_url (str): The URL of the book's main page.

        Returns:
            list: List of page URLs.
        """
        response = requests.get(book_url, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad responses
        html = HTMLParser(response.text)
        book_urls = [a.attributes.get('href', '')
                     for a in html.css('a.ld-item-name')]
        print(len(book_urls), "page urls found")
        return book_urls

    def get_cate_id(self, category_name: list) -> int:
        """
        Get the category ID for a given category name.

        Args:
            category_name (list): List of category name strings.

        Returns:
            int: Category ID.
        """
        with importlib.resources.files('bookspointer').joinpath('categories.json').open('r', encoding='utf-8') as file:
        # with open('bookspointer/bookspointer/categories.json', 'r', encoding='utf-8') as file:
            categories = json.load(file)
            category_name = ' '.join(category_name)
        for category in categories:
            if category['label'] == category_name:
                return category['id']
            elif 'ইতিহাস' in category_name:
                return 1
            elif 'কৌতুক' in category_name:
                return 2
            elif 'উপন্যাস' in category_name:
                return 3
            elif "থ্রিলার রহস্য রোমাঞ্চ অ্যাডভেঞ্চার" in category_name:
                return 4
            elif 'গল্পগ্রন্থ' in category_name:
                return 5
            elif 'গল্পের বই' in category_name:
                return 5
            elif "Editor's Choice" in category_name:
                return 5
            elif "ভ্রমণ কাহিনী" in category_name:
                return 6
            elif "বৈজ্ঞানিক কল্পকাহিনী" in category_name:
                return 9
            elif "ধর্ম ও দর্শন" in category_name:
                return 10
            elif "ইসলামিক বই" in category_name:
                return 10
            elif "ধর্মীয় বই" in category_name:
                return 10
            elif "সংস্কৃত" in category_name:
                return 10
            elif "কাব্যগ্রন্থ / কবিতা" in category_name:
                return 12
            elif "প্রবন্ধ ও গবেষণা" in category_name:
                return 13
            elif "রচনা" in category_name:
                return 13
            elif "কিশোর সাহিত্য" in category_name:
                return 14
            elif "আত্মজীবনী ও স্মৃতিকথা" in category_name:
                return 15
            elif "আত্মউন্নয়নমূলক বই" in category_name:
                return 15
            elif "নাটক" in category_name:
                return 16
            elif "গোয়েন্দা" in category_name:
                return 18
            elif "ভৌতিক" in category_name:
                return 19
            elif "হরর" in category_name:
                return 19
            elif "ভূতের বই" in category_name:
                return 19
            else:
                return 20
        return 20

    def get_book_list(self, author_url: str) -> list:
        """
        Scrape the list of books for a given author URL.

        Args:
            author_url (str): The URL of the author's page.

        Returns:
            list: List of dictionaries with book info (title, author, link).
        """
        books = []
        try:
            response = requests.get(author_url, headers=self.headers)
            html = HTMLParser(response.text)
            book_elements = html.css('article.entry-archive')
            print(f'{len(book_elements)} books found for the author.')
            for book in book_elements:
                title_ele = book.css_first(
                    'a.entry-title-link').text(strip=True)
                title = title_ele.split('–')[0].strip(
                ) if '–' in title_ele else title_ele
                author = title_ele.split('–')[1].strip(
                ) if '–' in title_ele else 'Unknown Author'
                book_link = book.css_first(
                    'a.entry-title-link').attributes.get('href', '')
                books.append({
                    'title': title,
                    'author': author,
                    'link': book_link
                })
            return books
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return []

    def get_book_details(self, book_info: dict, author_id: int = 1) -> list:
        """
        Scrape detailed information for a given book.

        Args:
            book_info (dict): Dictionary with book info (title, author, link).
            author_id (int, optional): ID of the author. Defaults to 1.

        Returns:
            list: List of dictionaries with detailed book data.
        """
        books = []
        try:
            response = requests.get(book_info['link'], headers=self.headers)
            response.raise_for_status()  # Raise an error for bad responses
            html = HTMLParser(response.text)
            book_ele = html.css_first('h1.page-header-title').text(strip=True)
            title = book_ele.split('–')[0].strip(
            ) if '–' in book_ele else 'Unknown Title'
            if title == 'Unknown Title':
                title = html.css_first('h1.page-header-title').text(strip=True)
            category = [cat.text(strip=True) for cat in html.css(
                'span.entry-terms-ld_course_category a')]
            cate_id = self.get_cate_id(category_name=category)
            try:
                series = html.css_first(
                    'span.entry-terms-series a').text(strip=True)
            except:
                series = category
            paragraphs = html.css_first('div.ld-tabs-content div')
            button = paragraphs.css_first('button')
            if button:
                button.decompose()
            content_str = ''  # str(paragraphs.html) if paragraphs else ''
            contents = [content_str]
            book_id = html.css_first(
                'div.ld-tab-content').attributes.get('id').split('-')[-1]
            book = {
                'book_id': book_id,
                'title': title,
                'author': book_info['author'],
                'author_id': author_id,
                'category': category,
                'category_id': cate_id,
                'series': series,
                'content': '',
                'url': book_info['link']
            }
            all_books_url = self.get_html_pages(book_info['link'])
            for idx, book_url in enumerate(all_books_url, start=1):
                new_content = self.get_book_content(book_url)
                if new_content:
                    if cate_id in self.single_page_cate:
                        book_copy = book.copy()  # or use copy.deepcopy(book) if nested dicts
                        book_copy['title'] = new_content['title']
                        book_copy['content'] = new_content['content']
                        book_copy['url'] = book_url
                        print(book_copy)
                        books.append(book_copy)
                    else:
                        contents.append(new_content.get('content', ''))
                print(
                    f"Page Processed {idx}/{len(all_books_url)}: Author ID: {author_id}")
            book['content'] = '<br/>'.join(contents)
            books.append(book)
            return books
        except requests.RequestException as e:
            print(f"An error occurred while fetching book details: {e}")
            return []

    def get_book_content(self, url: str) -> dict:
        """
        Scrape the content and title from a book page URL.

        Args:
            url (str): The URL of the book page.

        Returns:
            dict: Dictionary with 'content' and 'title', or None if failed.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            html = HTMLParser(response.text.replace('</p>', '</p><br/>'))
            content_div = html.css_first('div.ld-tabs-content > div')
            title = html.css_first('div.ld-focus-content h1').text(strip=True)
            for button in content_div.css('button'):
                button.decompose()
            if content_div:
                content_str = str(content_div.html)
                # print(content_str)
                return {'content': content_str, 'title': title}
        except requests.RequestException as e:
            print(f"An error occurred while fetching book content: {e}")
            return None
