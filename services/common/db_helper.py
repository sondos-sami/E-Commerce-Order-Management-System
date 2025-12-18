import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'database': 'ecommerce_system',
            'user': 'root',
            'password': 'MYSQL@2025#Krhps'
        }

    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None