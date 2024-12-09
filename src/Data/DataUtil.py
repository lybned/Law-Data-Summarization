from datasets import load_dataset

class DataUtil:
	def __init__(self):
		self.dataset = load_dataset("refugee-law-lab/canadian-legal-data", split="train")
	
	def get_train_data(self):
		return self.dataset