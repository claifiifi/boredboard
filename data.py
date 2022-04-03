#import os
#from distutils.util import execute
import psycopg2

#DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect('postgres://xwdyplbtpmigls:97f66622910198d15f3a546f0878eeb235a29fdaf8cfa28b119281a848034de2@ec2-54-158-247-97.compute-1.amazonaws.com:5432/d3t34o9801tarl', sslmode='require')
cur = conn.cursor()
'''
while True:
    quote=input("quote: ")
    author=input("author: ")
    cur.execute("INSERT INTO quotes (quote, author) VALUES (%s, %s)", (quote, author))
    conn.commit()
'''
'''cur.execute("CREATE TABLE boards (id serial PRIMARY KEY, name varchar);")'''
cur.execute("ALTER TABLE boards ADD COLUMN description varchar;")
#cur.execute("UPDATE posts SET board = %s;", (25,))
#cur.execute("CREATE TABLE quotes (quote varchar, author varchar);")
#cur.execute("UPDATE quoetes SET quote = %s WHERE author = %s;", ('무언가 자꾸 반복하다 보면 우리 자신이 그것이 됩니다.', '아리스토텔레스'))
#cur.execute("DELETE FROM boards WHERE id<25;")
cur.execute("UPDATE boards SET description=%s", ("첫번째 보드",))
cur.execute("SELECT * FROM boards;")
print(cur.fetchall())
'''cur.execute("SELECT * FROM posts;")
print(cur.fetchall())'''
conn.commit()
cur.close()
conn.close()
