from db.database import DataBase


class PaymentTable(DataBase):

    def __init__(self, db_file):
        super().__init__(db_file)


    async def add_pre_payment(self,label,user_id,amount,status,time_stamp):
        with self.connect:
            return self.cursor.execute('''INSERT INTO payment(user_id,label,amount,status,time_stamp)
                                          VALUES(?,?,?,?,?)''',
                                      [user_id,label,amount,status,time_stamp])
    async def add_payment(self,label,payment_method,invoice_id):
        with self.connect:
            return self.cursor.execute('''UPDATE payment SET payment_method=(?),invoice_id=(?) WHERE label=(?)''',
                                       [payment_method,invoice_id,label])

    async def get_invoice_id(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT invoice_id FROM payment WHERE label=(?)''',
                                       [label]).fetchone()[0]

    async def get_uncreation_payments(self):
        with self.connect:
            return self.cursor.execute('''SELECT label,user_id,time_stamp FROM payment
                                         WHERE status = 'active' AND payment_method IS NULL ''',
                                       ).fetchall()

    async def get_payment_id(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT id,time_stamp FROM payment
                                         WHERE label=(?) ''',
                                       [label]).fetchone()

    async def update_status(self,status,label):
        with self.connect:
            return self.cursor.execute('''UPDATE payment SET status=(?) WHERE label=(?)''',
                                       [status,label])

    async def check_status(self,status):
        with self.connect:
            return self.cursor.execute('''SELECT id,label,user_id,status,time_stamp FROM payment WHERE status=(?) ''',
                                       [status]).fetchall()

    async def change_status_payment(self,status,label):
        with self.connect:
            return self.cursor.execute('''UPDATE payment SET status=(?) WHERE label=(?)''',
                                       [status,label])

    async def get_payment_status(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT status FROM payment WHERE label=(?)''',
                                       [label]).fetchone()[0]

    async def get_payment_exists(self,label):
        with self.connect:
            data = self.cursor.execute('''SELECT id FROM payment WHERE label=(?)''',
                                       [label]).fetchone()
            return True if data else False

    async def delete_payment(self,label):
        with self.connect:
            return self.cursor.execute('''DELETE FROM payment WHERE label=(?)''',
                                       [label]).fetchall()

    async def get_payment_method_exist(self,label):
        with self.connect:
            data = self.cursor.execute('''SELECT payment_method FROM payment WHERE label=(?)''',
                                       [label]).fetchone()[0]

            return True if data else None

    async def get_payments(self,user_id,status):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM payment WHERE user_id = (?) AND status=(?)''',
                                       [user_id,status]).fetchall()

    async def get_payments_full(self, user_id, label):
        with self.connect:
            return self.cursor.execute('''SELECT payment.*, GROUP_CONCAT(product.category_id)
                                        FROM payment
                                        LEFT JOIN basket ON payment.id = basket.payment_id
                                        LEFT JOIN product ON basket.product_id = product.id
                                        WHERE payment.user_id = ? AND product.label = ?
                                        GROUP BY payment.id''', (user_id,label)).fetchone()

    async def get_payment_from_label(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM payment WHERE label=(?)''',
                                       [label]).fetchone()

    async def get_paid_payment(self,status):
        with self.connect:
            return self.cursor.execute('''SELECT label,user_id,payment_method,amount,time_stamp FROM payment
                                          WHERE status = (?)
                                          ORDER BY time_stamp DESC
                                        ''',
                                       [status]).fetchall()

    async def get_payment_from_user_label(self,user_id,label):
        with self.connect:
            return self.cursor.execute('''SELECT id,status,time_stamp FROM payment
                                           WHERE user_id = (?) AND label = (?)
                                       ''',[user_id,label]).fetchone()




