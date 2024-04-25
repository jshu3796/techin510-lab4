import psycopg2

class Database:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)

    def create_books_table(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    price NUMERIC,  # Changed to NUMERIC for easier sorting and filtering
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
            ''', (book['title'], float(book['price'].strip('£')), book['description'], book['rating']))  # Ensure price is converted to float
            self.conn.commit()
