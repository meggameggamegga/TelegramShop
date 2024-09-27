from db.database import DataBase


class PriceTable(DataBase):

    def __init__(self,db_file):
        super().__init__(db_file)

    async def get_price(self,server_id,category_id):
        with self.connect:
            data = self.cursor.execute('''SELECT price FROM price WHERE server_id=(?) AND category_id=(?)''',
                                       [server_id,category_id]).fetchone()[0]
            return data
    async def get_category_server_price(self):
        with self.connect:
            return self.cursor.execute('''
                SELECT price.id,
                       price.price,
                       category.id,
                       category.name,
                       server.id,
                       server.name
                FROM price
                JOIN server ON price.server_id = server.id
                JOIN category ON price.category_id = category.id
                GROUP BY category.id,server.id
            ''').fetchall()