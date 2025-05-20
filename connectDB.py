import mysql.connector
from mysql.connector import Error

def connect_mysql(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='BI'
):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            print("✅ Đã kết nối tới MySQL thành công.")
            return conn
    except Error as e:
        print(f"❌ Lỗi kết nối: {e}")
        return None
