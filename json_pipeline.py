import os
import json
class JsonPipeline:
    def __init__(self, 
                 generate_func, 
                 k:int, data_path:str, 
                 out_path:str):
        self.generate_func = generate_func
        self.k = k
        self.out_path = out_path
        self.done = False
        #check data path is json and exists

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data path {data_path} does not exist.")
        if not data_path.endswith('.json'):
            raise ValueError(f"Data path {data_path} is not a JSON file.")
        self.data_path = data_path
       
        next_entry = self._recovery(out_path)
        self.data = self.load_input_data()
        if next_entry == len(self.data):
            print("Output file already complete. No entries to process.")
            self.done = True
            return
        
        self.data = self.data[next_entry:]
        print(f"Resuming from entry {next_entry}")

    # load input path as json
    def load_input_data(self):
        import json
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        return data
    
    #check first if outpath exists if yes check the last json object in the data array
    def _recovery(self, out_path:str):
        self.result_data = []
        if os.path.exists(out_path):
            with open(out_path, 'r') as f:
                data = json.load(f)
                self.result_data = data
            if len(data) > 0:
                last_entry = len(data)
                return last_entry
        return 0
    
    
    def _generate_response(self, data):
        responses = []
        for _ in range(self.k):
            response = self.generate_func(data)
            responses.append(response)
        return responses
    
    def evaluate(self):
        if self.done:
            print("Evaluation already complete. Exiting.")
            return
        for data_entry in self.data:
            responses = self._generate_response(data_entry)
            #add the responses to the data entry
            data_entry['generate_data'] = responses
            self.result_data.append(data_entry)
            #replace all the data in the path
            with open(self.out_path, 'w') as f:
                json.dump(self.result_data, f, indent=4)
        if len(self.result_data) == len(self.load_input_data()):
            self.done = True
        else:
            Warning("Evaluation incomplete, some entries were not processed.")