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
		return eval_sum[0]
