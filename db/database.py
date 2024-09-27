import sqlite3

class DataBase:

    def __init__(self,db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def create_tables(self):

        with self.connect:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_id INTEGER,
                                    user_name TEXT,
                                    balance INTEGER DEFAULT 0
                                )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS category (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT
                                )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS product (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    login TEXT UNIQUE,
                                    password TEXT,
                                    category_id INTEGER,
                                    server_id INTEGER,
                                    status TEXT DEFAULT 'available',
                                    reserved_id INTEGER NULL,
                                    label INTEGER NULL,
                                    checked INTEGER DEFAULT (0),
                                    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE,
                                    FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE,
                                    FOREIGN KEY (reserved_id) REFERENCES user(id) ON DELETE CASCADE
                                )''')
            # FOREIGN KEY (category_id) REFERENCES category(id) - внешний ключ (category_id) ссылается на таблицу (category) на поле (id)


            self.cursor.execute('''CREATE TABLE IF NOT EXISTS server (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                name TEXT
                                            )''')

            self.cursor.execute('''CREATE TABLE IF NOT EXISTS basket (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                product_id INTEGER,
                                                user_id INTEGER,
                                                payment_id TEXT,
                                                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
                                                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                                                FOREIGN KEY (payment_id) REFERENCES payment(id) ON DELETE CASCADE
                                        )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS price (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        price INTEGER,
                                                        category_id INTEGER,
                                                        server_id INTEGER,
                                                        FOREIGN KEY (server_id) REFERENCES server(id) ON DELETE CASCADE,
                                                        FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
                                                        
                                                    )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS payment (
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            label TEXT,
                                                            user_id INTEGER,
                                                            payment_method TEXT,
                                                            amount INTEGER,
                                                            status TEXT,
                                                            invoice_id TEXT,
                                                            time_stamp TEXT,
                                                            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
                                                        )''')


    async def user_exist(self,user_id):
        with self.connect:
            user = self.cursor.execute('''SELECT user_id FROM user WHERE user_id=(?)''',
                                       [user_id]).fetchone()
            return True if user else False

    async def add_user(self,user_id,username):
        with self.connect:
            return self.cursor.execute('''INSERT INTO user(user_id,user_name) VALUES (?,?)''',
                                       [user_id,username])

    async def get_user(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT id FROM user WHERE user_id=(?) ''',
                                       [user_id]).fetchone()[0]

    async def get_user_id(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT user_id FROM user WHERE id=(?) ''',
                                       [user_id]).fetchone()[0]

    async def get_categories_with_products(self):
        with self.connect:
            result = self.cursor.execute('''
                SELECT
                    category.id AS category_id,
                    category.name AS category_name,
                    server.name AS server_name,
                    product.id AS product_id,
                    product.login AS product_login,
                    product.password AS product_password,
                    COUNT(product.id) AS product_count,
                    price.price AS product_price
                FROM
                    category
                JOIN
                    product ON category.id = product.category_id
                JOIN
                    server ON product.server_id = server.id
                LEFT JOIN
                    price ON product.server_id = price.server_id AND product.category_id = price.category_id
                GROUP BY
                    category.id, server.id, product.id
                ORDER BY
                    category.id, server.id, product.id
            ''').fetchall()

            return result

    async def get_server_categories_with_products_and_prices(self):
        with self.connect:
            result = self.cursor.execute('''
                SELECT
                    server.id AS server_id,
                    server.name AS server_name,
                    category.id AS category_id,
                    category.name AS category_name,
                    COUNT(product.id) AS product_count,
                    COALESCE(SUM(price.price), 0) AS total_price
                FROM
                    server
                LEFT JOIN
                    product ON server.id = product.server_id
                LEFT JOIN
                    category ON product.category_id = category.id
                LEFT JOIN
                    price ON product.server_id = price.server_id AND product.category_id = price.category_id
                WHERE product.status = "available"
                GROUP BY
                    server.id, category.id
                ORDER BY
                    server.id, category.id
            ''').fetchall()

            return result

    async def get_balance(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT balance FROM user WHERE user_id=(?)''',
                                       [user_id]).fetchone()[0]

    async def change_balance(self,user_id_table,balance):
        with self.connect:
            return self.cursor.execute('''UPDATE user SET balance=(?) WHERE id =(?)''',
                                       [balance,user_id_table]).fetchone()

    async def get_users(self):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM user''').fetchall()

    async def get_username(self,user_id_table):
        with self.connect:
            return self.cursor.execute('''SELECT user_name FROM user WHERE id=(?)''',
                                       [user_id_table]).fetchone()[0]