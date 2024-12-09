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

def get_previous(list, index):
    return list[index -1]
	
	
class InfoUtil:
	def __init__(self):
		pass
		
	def get_basic_info(self, input_text):
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
		return [Plaintiff, Defendant, Date]
	