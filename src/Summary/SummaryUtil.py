from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from config import *
import os
import time
import json

def extract_text_between_braces(input_string):
    if ( not ("{" in input_string and "}" in input_string) ):
        return ""
    """
    Extracts the text between the first '{' and the last '}' in a given string.
    
    Args:
        input_string (str): The string to extract text from.

    Returns:
        str: The extracted text, or an empty string if braces are not found.
    """
    start_index = input_string.find("{")
    end_index = input_string.rfind("}")
    
    # If either brace is not found, return an empty string
    if start_index == -1 or end_index == -1 or start_index > end_index:
        return ""
    
    return input_string[start_index:end_index + 1]

def process_input(input_data):
    if isinstance(input_data, str):
        return input_data
    elif isinstance(input_data, list):
        return ' '.join(map(str, input_data))
    elif isinstance(input_data, dict):
        return '\n'.join([f"- {key}: {value}" for key, value in input_data.items()])

os.environ["OPENAI_API_BASE"] = api_url
os.environ["OPENAI_MODEL_NAME"] = model_name  # Adjust based on available model
os.environ["OPENAI_API_KEY"] = api_key
summarizer_summary = Agent(
	role='Summarizer',
	goal="Provide the summary of the following document with the following attribute in a json format: location, case_type, jurisdiction, backgrounds, counsel, final_decision, specific_order",
	backstory=(
		"Equipped with advanced summarization techniques, "
		"the goal is to distill complex information into concise summaries."
	),
	allow_delegation=False,
	#llm="gpt-4"
)

# Create a task that requires code execution
summary_task = Task(  
	description='''Summarize the document based on the goal: {document}''',
	expected_output="A json as the result containing the following attributes from the text: location, case_type, jurisdiction, backgrounds, counsel, final_decision, specific_order. Make sure all values are in double quotes. Make sure all fields are either a string or a list of strings.",
	agent=summarizer_summary
)

crew_summary = Crew(
	agents=[summarizer_summary],
	tasks=[summary_task],
	verbose=True,
	memory=False,
	#respect_context_window=True  # enable by default
)

rate_summary_json = Agent(
	role='Evaluator',
	goal="Evaluate how good the summary json is compare to the original.",
	backstory="You are specialized in evaluating summary json based on the quality compared to the original text.",
	max_rpm=5,
	max_iter=3,
	allow_delegation=False,
)

eval_summary_task = Task(
	description="Give me a rating out of 10 based on the quality of the summary and the original text. \nOriginal: {original}. \nSummary Json: {summary}",
	expected_output="A score out of 10 with 10 being the best and 0 being the worst. The score represents the quality of the summary json compared to the original text. Do not include any suggestions.",
	agent=rate_summary_json
)

crew_eval_summary = Crew(
	agents=[rate_summary_json],
	tasks=[eval_summary_task],
	verbose=True,
	memory=False,
)
def extract_sublist(strings):

	strings_block = strings.split("\n")
	# Find indices
	start_index = next((i for i, s in enumerate(strings_block) if s.startswith("[") or s.lower().startswith("member:")), None)
	end_index = next((i for i, s in enumerate(strings_block) if s.startswith("Original signed") or s.startswith("\"Original signed") or s.startswith("Signed by") or s.lower().startswith("tribunal file")), None) # TRIBUNAL FILE

	# Return the sublist if valid indices are found
	if start_index is not None and end_index is not None and start_index <= end_index:
		return "\n".join(strings_block[start_index:end_index + 1])
	return ""  # Return an empty list if conditions are not met
	
	
# Prompt = "Provide the summary of the following document. Make sure to include arguments and reasoning from both sides if any. Make sure to also include who are involved. Make sure to include the result of the case if any."


class SummaryUtil:
	def __init__(self):
		pass
	
	def get_summary(self, input_text):
		text_list = []
		for case in input_text:
			text = case# dataset[i]["unofficial_text"]
			text_break = text.split("\n")
			#print(text)
			text_list.append(
				{"document": text}
			)
		guess_list_summary = []
		# Execute the crew
		result = crew_summary.kickoff_for_each(inputs=text_list)

		for r in result:
			cleaned = dict(r)['raw'].strip()
			guess_list_summary.append(cleaned)
			
		Cont = True
		# Guess content
		again_result = guess_list_summary

		# original text index
		again_list_old = list(range(0,len(again_result) + 1))


		attempts = []
		attempts.append(guess_list_summary)
		Count = 0
		while Cont and Count < 4:
			time.sleep(3)
			Count += 1
			again_list = []
			for i in range(len(guess_list_summary)):
				if (not ("{" in guess_list_summary[i] and "}" in guess_list_summary[i])):
					again_list.append(i)
			
			if (len(again_list) == 0):
				Cont = False
			else:
			
				#Set up data

				again_text = []
				for index in again_list:
					again_text.append(
					{"document": dataset[index]["unofficial_text"]}
					)
					
				# cleaner result
				again_result = crew_basic_info.kickoff_for_each(inputs=again_text)
				temp = []
				for aa in again_result:
					temp.append(dict(aa)['raw'].strip())
				again_result = temp.copy()
				attempts.append(again_result)
				# again_result= ["{}", "{}", "{}"]
				
				# Put the result back in the list
				for j in range(len(again_list)):
					guess_list_summary[again_list[j]] = again_result[j]
			
			
		final_summary_list = []
		final_summary_rating = []
		final_json_number = -1
		for i, r in enumerate(guess_list_summary):
			eval_json = [{
			"original": r,
			"summary": text_list[i]["document"]
			}]

			eval_sum = crew_eval_summary.kickoff_for_each(inputs=eval_json)
			#print(eval_sum)
			#print(eval_sum[0])
			
			clean_eval = str(eval_sum[0]).strip() #dict(eval_sum)['raw'].strip()
			#print("-- BEGIN --")
			#print(clean_eval)
			#print("-- END OF EVAL --")
			final_summary_rating.append(clean_eval)
			all_text = ""
			extracted = extract_text_between_braces(r)
			if (extracted != ""):
				extracted_dict = json.loads(extracted)
				final_json_number = len(extracted_dict)
				for key in extracted_dict:
					temp_text = f"{key}: {process_input(extracted_dict[key])} \n"
					all_text += temp_text
			#print(all_text)  
			#print("----END OF SUMMARY--------")
			final_summary_list.append(all_text)

		return final_summary_list, final_summary_rating