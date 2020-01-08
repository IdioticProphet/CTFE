import records

class SQL_Connect:
    def __init__(self, host="localhost", databasename="ctfengine", port=3306, user="root", password=''):
        self.connection = records.Database(f"mysql+pymysql://{user}:{password}@{host}:{port}/{databasename}")

def create_tables():
                # This function creates the tables if they do not already exist
                
                problems =  """
                CREATE TABLE IF NOT EXISTS problems(
                        unique_id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                        problem_name varchar(255) NOT NULL UNIQUE,
                        short_summary varchar(255) NOT NULL UNIQUE,
                        summary text NOT NULL,
                        category varchar(255)
                )
                """
                problem_check = """
                CREATE TABLE IF NOT EXISTS problem_check (
                        unique_id INT,
                        flag varchar(60) NOT NULL,
                        score INT NOT NULL,
                        PRIMARY KEY (unique_id),
                        FOREIGN KEY (unique_id) REFERENCES problems(unique_id)
                );
                """
                scoring_feed = """
                CREATE TABLE IF NOT EXISTS scoring_feed(
                        team_name varchar(255),
                        problem_solved varchar(255),
                        point_value INT,
                        new_total INT,
                        when_solved datetime DEFAULT CURRENT_TIMESTAMP
                )
                """
                users = """
                CREATE TABLE IF NOT EXISTS users(
                        id INT AUTO_INCREMENT,
                        name varchar(50) NOT NULL UNIQUE,
                        display_name varchar(100) NOT NULL UNIQUE,
                        email varchar(100) NOT NULL UNIQUE,
                        password varchar(94) NOT NULL,
                        team_id int(11) DEFAULT 0,
                        primary key (id)
                )
                """
                admin_table = """
                CREATE TABLE IF NOT EXISTS admins(
                        id INT,
                        PRIMARY KEY (id),
                        FOREIGN KEY (id) REFERENCES users(id)
                )
                """
                teams = """
                CREATE TABLE IF NOT EXISTS teams(
                        team_id int(11) PRIMARY KEY AUTO_INCREMENT,
                        team_name varchar(255) NOT NULL,
                        members TEXT NOT NULL,
                        score int(10) UNSIGNED NOT NULL DEFAULT 0,
                        team_password varchar(94) NOT NULL
                )
                """
                team_solves = """
                CREATE TABLE IF NOT EXISTS team_solves(
                        solve_number INT PRIMARY KEY AUTO_INCREMENT,
                        team_id int,
                        unique_id int,
                        FOREIGN KEY (team_id) REFERENCES teams(team_id),
                        FOREIGN KEY (unique_id) REFERENCES problems(unique_id)
                )
                """
                
                #make_admin_user = "INSERT INTO users(name, email, password, display_name) VALUES ('admin', 'admin@gmail.com', 'pbkdf2:sha256:150000$58B6AhrM$5d7b8b9315aa28a32ea41e5ab75c36a7784ba05d9e21001fcfd25399e263a8e1', 'admin')"
                #add_admin_user = "INSERT INTO admins (id) values (1)"
                tables = (problems, problem_check, scoring_feed, users, admin_table, teams, team_solves)#, make_admin_user, add_admin_user)
                sql_connection = SQL_Connect()
                for table in tables:
                        sql_connection.connection.query(table)
                        print(f"created table with defintion {table}")

if __name__ == "__main__":
    create_tables()
