
from src.Data.DataUtil import *
from src.Info.InfoUtil import *
from src.Summary.SummaryUtil import *
from src.Question.QuestionUtil import *
import sqlite3
from datetime import datetime


if __name__ == "__main__":
	print("Main Running...")
	
	data = DataUtil()

	
	basic_info = InfoUtil()
	train_data = data.get_train_data()
	summarize = SummaryUtil()
	question = QuestionUtil()
	legal_text = [train_data[10]["unofficial_text"]]
	#print(train_data[10]["unofficial_text"])	

	try:
		with open(file_path, "r", encoding="utf-8") as file:
			legal_text = [file.read()]
	except:
		legal_text = [train_data[10]["unofficial_text"]]
	

	basic_info = basic_info.get_basic_info(legal_text)
	#print(basic_info)
	summary_json = summarize.get_summary(legal_text)
	#print(summary_json)
	ask = input("What question to ask?") #"What advice can you give based on the case?"
	answered = question.answer_question(legal_text, ask)
	#print(answered)

	for i in range(len(summary_json[0])):
		final_info_list = basic_info[0]
		finao_info_eval = basic_info[1]
		final_summary_list = summary_json[0]
		final_summary_rating = summary_json[1]


		print("Basic Info:")
		print(final_info_list[i])
		print("\n")

		print("Basic Info Accuracy:")
		print(finao_info_eval[i]["accuracy"])
		print("\n")


		print("Short Summary:")
		print(final_summary_list[i])
		print("\n")

		#print("Summary Fields:")
		#print(f"Expected: 7, Got:{final_json_number}")
		#print("\n")

		print("Summary Feedback/Rating:")
		print(final_summary_rating[i])
		print("\n")

		print("Question Asked:")
		print(ask)
		print("Answer:")
		print(answered)