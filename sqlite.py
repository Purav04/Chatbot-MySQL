import sqlite3

# coneect to sqlite
connection_2_sql = sqlite3.connect("student.db")

# create cursor
cursor = connection_2_sql.cursor()

# create the table
table_info = """
create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT)
"""

cursor.execute(table_info)

# insert records
cursor.execute("""Insert Into STUDENT values('Purav', 'Data Science', 'A', 95)""")
cursor.execute("""Insert Into STUDENT values('Krish', 'DevOps', 'B', 86)""")
cursor.execute("""Insert Into STUDENT values('Johnny', 'Full Stack', 'A', 82)""")
cursor.execute("""Insert Into STUDENT values('Viper', 'DevOps', 'C', 99)""")
cursor.execute("""Insert Into STUDENT values('Mortal', 'UI/UX', 'A', 97)""")

# Display all the records
print("The inserted recordsare")
data = cursor.execute("""Select * from STUDENT""")
for row in data:
    print(row)

# Commit your changes in the database
connection_2_sql.commit()
connection_2_sql.close()
