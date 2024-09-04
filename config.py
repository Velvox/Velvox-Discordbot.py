import pymysql.cursors
import pymysql
# Discord Configuration
BOT_TOKEN = 'yourdiscordtoken'
# MySQL Database Configuration
MYSQL_HOST = "yourdatabasehost" # MySQL database host IP
MYSQL_USER = "yourdatabaseuser" # MySQL user
MYSQL_PASSWORD = "yourdatabasepassword" # MySQL password
MYSQL_DATABASE = "yourdatabasename" # MySQL database name
# Database connections
def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
def get_db_connection_tickets():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )
db_config = {
   'host': MYSQL_HOST, # MySQL database host IP
   'user': MYSQL_USER, # MySQL user
   'password': MYSQL_PASSWORD, # MySQL password
   'database': MYSQL_DATABASE # MySQL database name
}
