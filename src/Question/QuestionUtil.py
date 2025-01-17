from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from config import *
import os
import time
import json


answer_question_agent = Agent(
	role='Evaluator',
	goal="Answer the given question based on the provided legal case.",
	backstory="You are specialized in answering questions regarding legal cases.",
	max_rpm=5,
	max_iter=3,
	allow_delegation=False,
)

answer_question_task = Task(
	description="Answer the question based on the provided legal case \Legal Case: {case}. \nQuestion: {question}",
	expected_output="A serious answer regarding the question with the legal case as context.",
	agent=answer_question_agent
)

crew_answer_question= Crew(
	agents=[answer_question_agent],
	tasks=[answer_question_task],
	verbose=True,
	memory=False,
)

answer_eval_agent = Agent(
	role='Evaluator',
	goal="Evaluate how good the answer is based on the question and its legal case.",
	backstory="You are specialized in answering questions regarding legal cases.",
	max_rpm=5,
	max_iter=3,
	allow_delegation=False,
)

answer_eval_task = Task(
	description="Give a rating out of 10 based on the quality of the answer towards the question asked on the legal case. \nLegal Case: {case}. \nQuestion: {question} \nAnswer: {answer}",
	expected_output="A score out of 10 with 10 being the best and 0 being the worst. The score represents the quality of the answer towards the question. Do not include any suggestions.",
	agent=answer_eval_agent
)

crew_answer_eval= Crew(
	agents=[answer_eval_agent],
	tasks=[answer_eval_task],
	verbose=True,
	memory=False,
)


class QuestionUtil:
	def __init__(self):
		pass
	
	def answer_question(self, input_text, question):
		text_list = []
		for case in input_text:
			text = case# dataset[i]["unofficial_text"]
			text_break = text.split("\n")
			#print(text)
			text_list.append(
				{
				"case":case,
				"question": question
			}
			)
		eval_sum = crew_answer_question.kickoff_for_each(inputs=text_list)
		clean_answer = str(eval_sum[0]).strip()
		text_list_2 = []
		for case in input_text:

			text_list_2.append(
				{
				"case":case,
				"question": question,
				"answer":clean_answer
			})
		eval_result = crew_answer_eval.kickoff_for_each(inputs=text_list_2)
		clean_eval = str(eval_result[0]).strip()
		return clean_answer, clean_eval
	
