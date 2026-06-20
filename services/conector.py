import mysql.connector

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='biblioteca'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

con = connect_to_database()
if con:
    print("Connection successful!")    