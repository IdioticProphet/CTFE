from flask import current_app
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

	def create_tables(self):
                # This function creates the tables if they do not already exist
                ctf_problem_check = """
                CREATE TABLE IF NOT EXISTS ctf_problem_check(
                id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                unique_id varchar(10) NOT NULL,
                flag varchar(30) NOT NULL,
                score int(11) NOT NULL
                )
                """
                ctf_problems =  """
                CREATE TABLE IF NOT EXISTS ctf_problems(
                id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                problem_name varchar(255) NOT NULL UNIQUE,
                short_summary varchar(255) NOT NULL,
                summary text NOT NULL,
                unique_id varchar(10) NOT NULL UNIQUE,
                category varchar(255)
                )
                """
                scoring_feed = """
                CREATE TABLE IF NOT EXISTS scoring_feed(
                team_name varchar(255),
                problem_solved varchar(255),
                point_value int(11),
                when_solved datetime CURRENT_TIMESTAMP
                )
                """
                team_solves = """
                CREATE TABLE IF NOT EXISTS team_solves(
                team_id int(11)
                )
                """
                teams = """
                CREATE TABLE IF NOT EXISTS teams(
                id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                team_name varchar(255) NOT NULL,
                members TEXT NOT NULL,
                score int(10) UNSIGNED NOT NULL DEFAULT 0,
                team_password TEXT NOT NULL
                )
                """
                users = """
                CREATE TABLE IF NOT EXISTS users(
                id int(11) NOT NULL PRIMARY KEY,
                name varchar(50) NOT NULL,
                email varchar(50) NOT NULL,
                password varchar(94) NOT NULL,
                is_admin tinyint(1) DEFAULT 0,
                team_id int(11) DEFAULT 0
                )
                """
                basic_problem = "INSERT INTO ctf_problems(problem_name, short_summary, summary, unique_id, category) VALUES ('My First Problem!', 'Intro Problem', 'Welcome to CTFE, my ctf platform that comes after d, doesnt mean its better though!', '1', 'basic')"
                make_admin_user = "INSERT INTO users(name, email, password, is_admin) VALUES ('admin', 'admin@gmail.com', 'pbkdf2:sha256:150000$58B6AhrM$5d7b8b9315aa28a32ea41e5ab75c36a7784ba05d9e21001fcfd25399e263a8e1', '1')"
                tables = (ctf_problem_check, ctf_problems, scoring_feed, team_solves, teams_users, basic_problem, make_admin_user)
                for table in tables:
                        self.connection.query(table)
                        current_app.logger.info(f"Ran SQL command to create tables, defition, {table}")
