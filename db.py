from pymysql import connect, Connection
from pymysql.cursors import DictCursor

from environs import Env


env = Env()
env.read_env()

class Database:
    def __init__(
        self, 
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: int
    ) -> None:
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
    
    
    def get_connection(self) -> Connection:
        return connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            cursorclass=DictCursor
        )

    def execute(self, sql: str, params = None, commit=False, fetchone=False, fetchall=False):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        
        if commit:
            connection.commit()
        
        
        if fetchall and fetchone:
            raise ValueError("Fetchall va Fetchone bir vaqtda yuborilishi mumkin emas")

        if fetchone:
            return cursor.fetchone()

        if fetchall:
            return cursor.fetchall()  
        
    def create_users_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                telegram_id VARCHAR(100) UNIQUE NOT NULL,
                fullname VARCHAR(100) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
                )
            """
        self.execute(sql=sql)
    
    
    def create_cities_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS cities(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                city_name VARCHAR(100) NOT NULL
                )
            """
        self.execute(sql=sql)
        
    def register_user(self, telegram_id: str, fullname: str):
        
        sql = f"""
            INSERT INTO users(telegram_id, fullname, created_at)
            VALUES (%s, %s, NOW()) 
            """
        self.execute(sql=sql, params=(telegram_id, fullname), commit=True)
        
    def get_user(self, telegram_id: str):
        sql = "SELECT id, telegram_id, fullname FROM users WHERE telegram_id=%s"
        return self.execute(sql=sql, params=(telegram_id,), fetchone=True)

   
    def delete_user(self, telegram_id: str):
        sql = "DELETE FROM users WHERE telegram_id=%s"
        self.execute(sql=sql, params=(telegram_id,), commit=True)
    
    def add_city(self, user_id: int, city_name: str) -> list[dict]:
        sql = """
        INSERT INTO cities (user_id, city_name)
        VALUES (%s, %s)  
        """
        self.execute(sql=sql, params=(user_id, city_name), commit=True)
    
    def get_user_cities(self, user_id: int) -> list[dict]:
        sql = """
        SELECT * FROM cities WHERE user_id=%s
        """
        return self.execute(sql=sql, params=(user_id,), fetchall=True)
    
    def clear_user_cities(self, user_id: int):
        sql = """
            DELETE FROM cities WHERE user_id = %s
        """
        self.execute(sql=sql, params=(user_id,), commit=True)
    
    
db = Database(
    db_name  = env.str("DB_NAME"),
    db_user  = env.str("DB_USER"),
    db_password = env.str("DB_PASSWORD"),
    db_host = env.str("DB_HOST"),
    db_port = env.int("DB_PORT"),
)

