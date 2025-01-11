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

def check_basic_info(check_dict, original_text):
    result = {"Exist": [], "Not Exist": []}
    for key in check_dict:
        item = check_dict[key]
        if isinstance(item, str):
            if (item in original_text):
                result["Exist"].append(item) 
            else:
                result["Not Exist"].append(item) 
        elif isinstance(item, list):
            for word in item:
                if (word in original_text):
                    result["Exist"].append(word) 
                else:
                    result["Not Exist"].append(word) 

    result["accuracy"] = str(round(len(result["Exist"]) / (len(result["Exist"]) + len(result["Not Exist"])) * 100, 2)) + "%"

    return result
    

def get_elements_between_markers(array):
    # Find indices of strings starting with "start" and "end"
    start_index = next((i for i, s in enumerate(array) if s.lower().startswith("date")), None)
    if (start_index != None):
        end_index = next((i for i, s in enumerate(array) if s.startswith("Respondent") and i > start_index), None)

        print(start_index, end_index)
        # Return the elements between "start" and "end"
        if start_index != None and end_index != None:
            return array[start_index:end_index + 1]
        return []
    else:
        return []

def process_input(input_data):
    if isinstance(input_data, str):
        return input_data
    elif isinstance(input_data, list):
        return ' '.join(map(str, input_data))
    elif isinstance(input_data, dict):
        return '\n'.join([f"- {key}: {value}" for key, value in input_data.items()])

def get_previous(list, index):
    return list[index -1]

class Info(BaseModel):
    date: str
    complainant: str
    respondent: str

os.environ["OPENAI_API_BASE"] = api_url
os.environ["OPENAI_MODEL_NAME"] = model_name  # Adjust based on available model
os.environ["OPENAI_API_KEY"] = api_key

get_basic_info = Agent(
    role='Data Extractor',
    goal="Extract desired information based on the description",
    backstory="You are specialized in extracting names and entities from a given text",
    max_rpm=5,
    max_iter=3,
    allow_delegation=False,
    #llm="gpt-4"
)

# Create a task that requires code execution
info_extraction_task = Task(  
    description="Extract the court date, complainant and respondent from the following text: {document}",
    expected_output="A json containing all the information asked in the description. There should only be a json in the final answer. The json contains the following fields 'court date', 'complainant' and 'respondent'. ",
    agent=get_basic_info,
    output_pydantic=Info,
)

crew_basic_info = Crew(
    agents=[get_basic_info],
    tasks=[info_extraction_task],
    verbose=True,
    memory=False,
)
	
class InfoUtil:
	def __init__(self):
		pass
		
	def get_basic_info(self, input_text):
		print(api_url)
		print(model_name)
		print(api_key)

		'''
		text = input_text.split("\n")
		result = get_elements_between_markers(text)
		if (len(result) == 0):
			return ["", "", ""]
		#print([i for i, value in enumerate(result) if value.startswith("Complainant")])
		index1 = [i for i, value in enumerate(result) if value.startswith("Complainant")]
		#print([i for i, value in enumerate(result) if value.startswith("Respondent")])
		index2 = [i for i, value in enumerate(result) if value.startswith("Respondent")]
		Plaintiff = get_previous(result, index1[0]) if len(index1) > 0 else "Unavailable"
		Defendant = get_previous(result, index2[0]) if len(index2) > 0 else "Unavailable"
		Date = result[1]
		print(Plaintiff, Defendant, Date)
		return [Plaintiff, Defendant, Date]'''
	

		guess_list = []
		actual_list = []
		text_list = []
		for legal_case in input_text:
			text = legal_case#dataset[i]["unofficial_text"]
			text_break = text.split("\n")
			#print(text)
			text_list.append(
				{"document": text}
			)
			
			'''
			result = get_elements_between_markers(text_break)
			if (len(result) == 0):
				print(text_break)

			else:
				#print(result)
				
				#print([i for i, value in enumerate(result) if value.startswith("Complainant")])
				index1 = [i for i, value in enumerate(result) if value.startswith("Complainant")]
				#print([i for i, value in enumerate(result) if value.startswith("Respondent")])
				index2 = [i for i, value in enumerate(result) if value.startswith("Respondent")]
				Plaintiff = get_previous(result, index1[0]) if len(index1) > 0 else "Unavailable"
				Defendant = get_previous(result, index2[0]) if len(index2) > 0 else "Unavailable"
				Date = result[1]
				#print(Plaintiff, Defendant, Date)
				actual_list.append([Plaintiff, Defendant, Date])'''
			
		# Execute the crew
		result = crew_basic_info.kickoff_for_each(inputs=text_list)
		#return result


		for r in result:
			cleaned = dict(r)['raw'].strip()
			guess_list.append(cleaned)
			
		Cont = True
		# Guess content
		again_result = guess_list

		# original text index
		again_list_old = list(range(0,len(again_result) + 1))

		attempts = []
		attempts.append(guess_list)
		Count = 0
		while Cont and Count < 4:
			time.sleep(3)
			Count += 1
			again_list = []
			for i in range(len(guess_list)):
				if (not ("{" in guess_list[i] and "}" in guess_list[i])):
					again_list.append(i)
			
			if (len(again_list) == 0):
				Cont = False
			else:
			
				#Set up data

				again_text = []
				for index in again_list:
					again_text.append(
						{"document": text_list[index]["document"]}
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
					guess_list[again_list[j]] = again_result[j]
			

		final_info_list = []
		finao_info_eval = []
		for i, r in enumerate(guess_list):

			all_text = ""
			#print(r)
			extracted = extract_text_between_braces(r)
			if (extracted != ""):
				#print(extracted)
				extracted_dict = json.loads(extracted)

				# Check the answer:
				result_check = check_basic_info(extracted_dict, text_list[i]["document"])
				finao_info_eval.append(result_check)
				#print(result_check)

				for key in extracted_dict:
					temp_text = f"{key}: {process_input(extracted_dict[key])} \n"
					all_text += temp_text
				#print(all_text)  
				#print("-----END OF BASIC INFO--------")
			final_info_list.append(all_text)

		return final_info_list, finao_info_eval