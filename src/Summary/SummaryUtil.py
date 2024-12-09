from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel

from config import *

import os

os.environ["OPENAI_API_BASE"] = api_url
os.environ["OPENAI_MODEL_NAME"] = model_name  # Adjust based on available model
os.environ["OPENAI_API_KEY"] = api_key

def extract_sublist(strings):

    strings_block = strings.split("\n")
    # Find indices
    start_index = next((i for i, s in enumerate(strings_block) if s.startswith("[") or s.lower().startswith("member:")), None)
    end_index = next((i for i, s in enumerate(strings_block) if s.startswith("Original signed") or s.startswith("\"Original signed") or s.startswith("Signed by") or s.lower().startswith("tribunal file")), None) # TRIBUNAL FILE

    # Return the sublist if valid indices are found
    if start_index is not None and end_index is not None and start_index <= end_index:
        return "\n".join(strings_block[start_index:end_index + 1])
    return ""  # Return an empty list if conditions are not met
	
	
Prompt = "Provide the summary of the following document. Make sure to include arguments and reasoning from both sides if any. Make sure to also include who are involved. Make sure to include the result of the case if any."


summarizer_receipt = Agent(
    role='Summarizer',
    goal="Provide the summary of the following document",
    backstory=(
        "Equipped with advanced summarization techniques, "
        "the goal is to distill complex information into concise summaries."
    ),
    allow_delegation=False,
    #llm="gpt-4"
)


# Create a task that requires code execution
data_analysis_task = Task(  
    description='''Summarize the document based on the goal: {document}''',
    expected_output="A concise summary of the recepit for the receipt.",
    agent=summarizer_receipt
)

crew = Crew(
    agents=[summarizer_receipt],
    tasks=[data_analysis_task],
    verbose=True,
    memory=False,
    #respect_context_window=True  # enable by default
)


class SummaryUtil:
	def __init__(self):
		pass
	
	def get_summary(self, text):

		Cont = True
		sum_text = text
		clean_text = extract_sublist(sum_text)
   
		Attempt = 0
		while (Cont and clean_text != "" and Attempt < 6):
			# Execute the crew
			result = crew.kickoff(inputs={"document": clean_text})
			result = dict(result)['raw'].strip()
			#result_list.append(result)
			#check_empty.append( (result == "") )
			if (result != "" and "[...]" not in result):
				Cont = False
				#result_list.append(result)
			Attempt += 1
			#print(result)
		return result