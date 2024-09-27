from db.database import DataBase


class CategoryTable(DataBase):

    def __init__(self,db_file):
        super().__init__(db_file)

    async def add_category(self,name):
        with self.connect:
            return self.cursor.execute('''INSERT INTO category(name) VALUES(?)''',
                                       [name])

    async def get_product_from_category(self,category_id,status='available'):

        '''
        :param category_id: - id from category_id
        :return: object from product (login and password)
        '''

        with self.connect:
            return self.cursor.execute('''SELECT product.id,server_id FROM product
                                          JOIN category ON product.category_id = category.id
                                          WHERE category.id =(?) AND status=(?)''',
                                          [category_id,status]).fetchall()


    async def get_all_categories(self):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM category''').fetchall()

    async def get_category(self,category_id):
        with self.connect:
            return self.cursor.execute('''SELECT name FROM category WHERE id=(?) ''',
                                       [category_id]).fetchone()[0]
