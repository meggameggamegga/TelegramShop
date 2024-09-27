from db.database import DataBase


class ProductTable(DataBase):

    def __init__(self, db_file):
        super().__init__(db_file)


    async def add_product(self,login,password,category_id,server_id):
        with self.connect:
            return self.cursor.execute('''INSERT INTO product(login,password,category_id,server_id) VALUES(?,?,?,?)''',
                                       [login,password,category_id,server_id])

    async def get_product(self,category_id):
        with self.connect:
            return self.cursor.execute('''SELECT login,password FROM product WHERE category_id =(?)''',
                                       [category_id]).fetchone()


    async def get_product_from_category(self,category_id):
        with self.connect:
            return self.cursor.execute('''SELECT login,password FROM product JOIN category ON product.category_id = category.id
                                          WHERE category_id =(?)''',
                                          [category_id]).fetchall()


    async def get_count_product(self,server_id,category_id,status='available'):
        with self.connect:
            products = self.cursor.execute('''SELECT id FROM product WHERE server_id = (?) AND category_id = (?)
                                              AND status = (?)''',
                                       [server_id,category_id,status]).fetchall()
            return len(products)

    async def reserve_product_for(self,product_id,reserved_id,status,label):
        with self.connect:
            return self.cursor.execute('''UPDATE product SET status=(?),reserved_id=(?),label=(?) WHERE id =(?)''',
                                       [status,reserved_id,label,product_id])

    async def get_active_choose_products(self,category_id,server_id,status='available'):
        with self.connect:
            return self.cursor.execute('''SELECT id FROM product WHERE status=(?) AND category_id=(?) AND server_id=(?)''',
                                       [status,category_id,server_id]).fetchall()

    async def get_reserved_products(self,status,reserved_id,label):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM product WHERE status=(?) AND reserved_id=(?) AND label=(?)''',
                                       [status,reserved_id,label]).fetchall()

    async def change_status(self,status,product_id):
        with self.connect:
            return self.cursor.execute('''UPDATE product SET status =(?) WHERE id = (?)''',
                                       [status,product_id])

    async def unreserved_product(self,status,label):
        with self.connect:
            return self.cursor.execute('''UPDATE product SET reserved_id=NULL,label=NULL,status=(?) WHERE label=(?)''',
                                       [status,label]).fetchall()

    async def get_reserve(self,status):
        with self.connect:
            return self.cursor.execute('''SELECT reserved_id,label FROM product WHERE status=(?)''',
                                       [status]).fetchall()

    async def get_user_products(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT category_id,server_id FROM product
                                          WHERE label = (?)''',
                                       [label]).fetchone()

    async def get_log_pas_label(self,label):
        with self.connect:
            return self.cursor.execute('''SELECT login,password,category_id,server_id FROM product
                                          WHERE label=(?)
                                      ''',[label]).fetchall()

    async def get_checked(self,label):
        with self.connect:
            data = self.cursor.execute('''SELECT checked FROM product
                                          WHERE label=(?)
                                      ''',[label]).fetchone()[0]
            return data

    async def set_checked(self,checked,label):
        with self.connect:
            return self.cursor.execute('''UPDATE product SET checked = (?)
                                          WHERE label=(?)
                                      ''',[checked,label])

