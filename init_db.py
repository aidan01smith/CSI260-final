import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Stock', 'Content for the first stock option')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Stock', 'Content for the second option')
            )

connection.commit()
connection.close()
