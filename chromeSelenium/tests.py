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
        print(int(str(user)[1:-2]))
        cur.execute('SELECT url FROM users WHERE user_id = %s', [user])
        print(''.join(cur.fetchone()))

aprnce_record()