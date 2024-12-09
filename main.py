
from src.Data.DataUtil import *
from src.Info.InfoUtil import *
from src.Summary.SummaryUtil import *
import sqlite3
from datetime import datetime

# Function to insert data into the table
def add_interaction(date, person1, person2, summary):
    cursor.execute("""
    INSERT INTO interactions (date, person1, person2, summary)
    VALUES (?, ?, ?, ?)
    """, (date, person1, person2, summary))
    conn.commit()

if __name__ == "__main__":
	print("Main Running...")
	data = DataUtil()
	basic_info = InfoUtil()
	train_data = data.get_train_data()
	summarize = SummaryUtil()

	print(len(train_data))
	
	basic_info_list = []
	summary_list = []
	for i in range(10):
		result = basic_info.get_basic_info(train_data[i]["unofficial_text"])
		print(result)
		basic_info_list.append(result)
	
	
	for j in range(10):
		summ = summarize.get_summary(train_data[j]["unofficial_text"])
		print(summ)
		summary_list.append(summ)
		
		
	conn = sqlite3.connect("relationships.db")
	# Create a table if it doesn't exist
	cursor.execute("""
	CREATE TABLE IF NOT EXISTS interactions (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		date TEXT NOT NULL,
		person1 TEXT NOT NULL,
		person2 TEXT NOT NULL,
		summary TEXT NOT NULL
	)
	""")
	conn.commit()
	
	for x in range(len(basic_info_list)):
		add_interaction(basic_info_list[x][1], basic_info_list[x][2], basic_info_list[x][0], summary_list[x])
