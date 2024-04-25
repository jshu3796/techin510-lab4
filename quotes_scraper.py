import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import psycopg2

# Define a class for interacting with the PostgreSQL database
class Database:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)

    def create_books_table(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    price VARCHAR(50),
                    description TEXT,
                    rating INTEGER
                );
            ''')
            self.conn.commit()

    def insert_book(self, book):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO books (title, price, description, rating)
                VALUES (%s, %s, %s, %s)
            ''', (book['title'], book['price'], book['description'], book['rating']))
            self.conn.commit()

# Load environment variables
load_dotenv()

BASE_URL = 'http://books.toscrape.com/catalogue/'
START_PAGE = 'http://books.toscrape.com/catalogue/page-1.html'
mydb = Database(os.getenv('DATABASE_URL'))
mydb.create_books_table()

def scrape_books(start_url):
    page = start_url
    while page:
        print(f"Scraping {page}")
        response = requests.get(page)
        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.select('article.product_pod h3 a')
        for book in books:
            book_url = BASE_URL + book['href']
            book_data = scrape_book_details(book_url)
            mydb.insert_book(book_data)
        next_button = soup.select_one('li.next a')
        page = BASE_URL + next_button['href'] if next_button else None

def scrape_book_details(url):
    print(f"Scraping book details from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.select_one('h1').text
    price = soup.select_one('.price_color').text
    description = soup.select_one('#content_inner > article > p').text
    word_to_num = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    rating_class = soup.select_one('p.star-rating')['class']
    rating = word_to_num.get(rating_class[1], 0)
    return {
        'title': title,
        'price': price,
        'description': description,
        'rating': rating
    }

scrape_books(START_PAGE)
