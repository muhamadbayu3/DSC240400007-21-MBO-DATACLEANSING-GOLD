import sqlite3

conn = sqlite3.connect('gold_chalange.db')
print("opened database successfuly")



conn.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, Text varchar(225), clean_text varchar(225));''')
print("Table 'users' created successfully")


conn.commit()
print("Records created successfuly")
conn.close()

