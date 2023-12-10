import psycopg2
from config import host, db_name, password, user

conn = psycopg2.connect(
    host=host,
    database=db_name,
    user=user,
    password=password
)
cur = conn.cursor()
conn.autocommit = True


def aprnce_record():
    cur.execute('SELECT user_id FROM users')
    users = cur.fetchall()
    for user in users:

        print(user)

aprnce_record()