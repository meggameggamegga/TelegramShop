from db.database import DataBase


class BasketTable(DataBase):

    def __init__(self,db_file):
        super().__init__(db_file)

    # Добавить товар пользователю в корзину
    async def add_products_to_user(self, user_id, product_id, payment_id):
        with self.connect:
            self.cursor.execute('''INSERT INTO basket(user_id, product_id, payment_id) VALUES (?,?,?)''',
                                [user_id, product_id, payment_id])

    async def get_product_from_basket(self,product_id):
        with self.connect:
            return self.cursor.execute('''SELECT product.* FROM product
                                          JOIN basket ON basket.product_id = product.id
                                          WHERE product.id = (?)''',
                                          [product_id]).fetchone()

    async def get_basket(self,user_id):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM basket WHERE user_id=(?)''',
                                       [user_id]).fetchall()

    async def get_basket_payment_info(self, user_id):
        with self.connect:
            return self.cursor.execute('''SELECT payment.label, payment.time_stamp,payment.payment_method,payment.amount FROM payment
                                          JOIN basket ON basket.payment_id = payment.id
                                          WHERE basket.user_id = (?)
                                        ''',
                                       [user_id]).fetchone()


    async def basket_product_group(self, user_id):
        with self.connect:
            return self.cursor.execute('''SELECT b.payment_id, 
                                              GROUP_CONCAT(b.product_id), 
                                              GROUP_CONCAT(b.user_id),
                                              p.label
                                        FROM basket b
                                        JOIN payment p ON b.payment_id = p.id
                                        WHERE b.user_id = ?
                                        GROUP BY b.payment_id, p.label;''', (user_id,)).fetchall()

    async def get_current_order(self, payment_id):
        with self.connect:
            return self.cursor.execute('''SELECT GROUP_CONCAT(basket.product_id), 
                                              GROUP_CONCAT(basket.user_id) 
                                        FROM basket 
                                        JOIN payment ON basket.payment_id = payment.id
                                        WHERE payment_id = ?''',
                                       (payment_id,)).fetchall()

    async def get_users_baskets(self):
        with self.connect:
            return self.cursor.execute('''SELECT user.user_name, COUNT(basket.product_id) AS product_count
                                          FROM basket
                                          JOIN user ON basket.user_id = user.id
                                          GROUP BY user.user_id,user.user_name;
                                        ''').fetchall()

    async def get_basket_user_label(self,user_id,payment_id):
        with self.connect:
            return self.cursor.execute('''SELECT id,user_id FROM basket
                                        WHERE payment_id = (?) AND user_id=(?)
                                        JOIN product ON basket.product_id = product.id
                                       ''',[payment_id,user_id]).fetchall()


