from db.database import DataBase



class ServerTable(DataBase):

    def __init__(self,db_file):
        super().__init__(db_file)

    async def add_server(self,server_name):
        with self.connect:
            return self.cursor.execute('''INSERT INTO server(name) VALUES(?)''',
                                       [server_name])

    async def get_all_servers(self):
        with self.connect:
            return self.cursor.execute('''SELECT * FROM server''').fetchall()

    async def get_server_name(self,server_id):
        with self.connect:
            return self.cursor.execute('''SELECT name FROM server WHERE id = (?)''',
                                       [server_id]).fetchone()[0]