import records

class SQL_Connect:
	def __init__(self, host="localhost", databasename="ctfengine", port=55555, user="root", password=""):
		self.connection = records.Database(f"mysql+pymysql://{user}:{password}@{host}:{port}/{databasename}")
	def disconnect(self):
		self.connection.close()
	def is_up(self):
		try:
                        self.connection.get_connection().open
                        return True
		except:
			return False
