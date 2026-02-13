import mysql.connector
import yaml

with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

db = mysql.connector.connect(
    host="localhost",
    user=config["sql"]["user"],
    passwd=config["sql"]["password"],
    database=config["sql"]["database"]
)

cursor = db.cursor()

# --------Create a database------------- 
# Run once then add to connect string
# cursor.execute("CREATE DATABASE standstill")

# --------------Create a table structure (slags excel ark table)----------------- 
# cursor.execute("CREATE TABLE Person (name VARCHAR(50), age smallint UNSIGNED, personID int PRIMARY KEY AUTO_INCREMENT)")

# ---GET the Person table created and its types. What does the table it self look like?---
#cursor.execute("DESCRIBE Person)
# You can also iterate on it.
# for x in cursor:
#     print(x)

# ---INSERT/add values into Table---
# cursor.execute("INSERT INTO Person (name, age) VALUES (%s,%s)", ("Joe", 56))
# db.commit()

# ---GET everything from my Person Table and interate over it in the console.---
# cursor.execute("SELECT * FROM standstillUser")
# for x in cursor:
#     print(x)

# ---- REMOVE STUFF -----   
# Remove one column from a Table
#cursor.execute("ALTER TABLE standstillUser DROP musicScore") # For eksempel..
#db.commit()

# Change the name of a column
#cursor.execute("ALTER TABLE standstillUser CHANGE musicScore musicScoreNew VARCHAR(50)") # For eksempel..
#db.commit()

# # Delete all rows from specific Table
# cursor.execute("DELETE from standstillUser")
# cursor.execute("DELETE from standstillRealTime")

# # When deleting all data, reset auto_increment to 1
# cursor.execute("ALTER TABLE standstillUser AUTO_INCREMENT = 1")
# cursor.execute("ALTER TABLE standstillRealTime AUTO_INCREMENT = 1")

# db.commit()

# Delete rows based on id from specific Table
# cursor.execute("DELETE from standstillUser where id = 2") # For eksempel..
# db.commit()

# Delete database (But remembe to remove the database string in the connectro string first!)
# cursor.execute("DROP DATABASE sakila")
#db.commit()



# --------- Creating the standstill Tables ----------------
    # Creating the Tables only needs to happen once. And I did it in the sql-cheasheet.py file.
    # try: # to create a table for storing real-time data in MySQL database
    #     cursor.execute(
    #                     """
    #                     CREATE TABLE standstillUser 
    #                     (
    #                     id INT unsigned NOT NULL AUTO_INCREMENT,
    #                     standstillUserID INT unsigned,
    #                     age INT unsigned, 
    #                     language VARCHAR(2),
    #                     musicScore FLOAT, 
    #                     silenceScore FLOAT,
    #                     feedbackMusic INT unsigned,
    #                     feedbackStandstill INT unsigned,
    #                     PRIMARY KEY (id)
    #                     )
    #                     """
    #                     )
    # except mysql.connector.errors.ProgrammingError:
    #     pass
    # try:
    #     cursor.execute(
    #                     """
    #                     CREATE TABLE standstillRealTime 
    #                     (
    #                     id INT unsigned NOT NULL AUTO_INCREMENT,
    #                     standstillUserID INT unsigned,
    #                     genre VARCHAR(50),
    #                     date TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    #                     w FLOAT(7,6) NOT NULL, 
    #                     PRIMARY KEY (id)  
    #                     )
    #                     """
    #                     )
    # except mysql.connector.errors.ProgrammingError:
    #     pass