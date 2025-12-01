class JudgeMajority:
    def __init__(self, generate_fn, max_retries=5):
        """
        generate_fn: A function that receives a prompt and returns the model's output text.
        max_retries: Number of attempts allowed for the model to return a valid T/F answer.
        """
        self.generate = generate_fn
        self.max_retries = max_retries

    def _get_valid_answer(self, prompt):
        """
        Calls the model repeatedly until a valid answer ('T' or 'F') is returned.
        Returns the validated answer as a capitalized string.
        Raises an error if no valid answer is produced after max_retries.
        """
        for _ in range(self.max_retries):
            raw_output = self.generate(prompt)
            if not raw_output:
                continue
            raw_output = raw_output.strip()
            answer = raw_output.upper()
            # print(f"prompt:\n {prompt}")
            # print(f"Processed answer: {answer}")
            # print("--" * 20)
            
            # Only allow exact 'TRUE' or 'FALSE'
            if "TRUE" in answer:
                return "TRUE"
            elif "FALSE" in answer:
                return "FALSE"

        # Model consistently failed to produce a valid answer
        raise ValueError(
            f"Model failed to produce 'TRUE' or 'FALSE' after {self.max_retries} attempts. "
            f"Last output: {raw_output}"
        )

    def judge(self, prompt, K):
        """
        Executes the judging process K times.
        Each iteration must produce a valid T/F answer.
        Returns True if majority of answers are 'T', otherwise False.
        Tie is resolved as False by default.
        """
        results = []

        for _ in range(K):
            answer = self._get_valid_answer(prompt)
            results.append(answer)

        # Count how many T and F responses were collected
        count_T = results.count("TRUE")
        count_F = results.count("FALSE")

        # Majority voting logic
        if count_T > count_F:
            return True
        elif count_F > count_T:
            return False
        else:
            # In case of a tie, return False (can be changed if needed)
            return False
        
from config import init_config

# init configurations
config = init_config()
config.init_env()
import json
import torch
from utils import load_model, generate
from models_factory import get_model_and_split_function
def construct_prompt(model_answer, correct_answer):
    return f"Correct answer: {correct_answer}\nModel answer: {model_answer}\nFollow instructions:\n1. Extract final answer.\n2. Compare.\n3. Output TRUE or FALSE only."
def get_next_data_row(data):
    for index, item in enumerate(data):
        generate_data = item["generate_data"]
        if "is_correct_judged" not in generate_data[0]:
            return index
    return len(data)


if __name__ == "__main__":
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.reset_accumulated_memory_stats()

    k = 5
    system_prompt = "You are a strict answer judge."
    path = "result/deepseek_r1_distill_qwen_7b/asdiv_evaluation_format.json"
    model_key = "deepseek_r1_distill_qwen_7b"
    gpu_id = 0  # default GPU id
    with open(path, "r") as f:
        data = json.load(f)
    start_index = get_next_data_row(data)
    if start_index >= len(data):
        print("All data has already been processed.")
        exit(0)
    print(f"Starting from index: {start_index} out of {len(data)}")
    data = data[start_index:]
    # print next data row for debug
    print(f"Next data row to process: {data[0]}")
    # load model
    model_name, split_function = get_model_and_split_function(model_key)    
    model_kwargs = {
        "dtype": torch.float16,
        "trust_remote_code": True,
        "use_cache": False,
    }
     # init mpdel
    tokenizer_kwargs = {}
    kwargs = {"model_kwargs": model_kwargs, "tokenizer_kwargs": tokenizer_kwargs}
    model, tokenizer = load_model(model_name, device_map=f"cuda:{gpu_id}", **kwargs)
    # Check the device of the model parameters
    device = next(model.parameters()).device
    print("Model device:", device)
    #check for a dir with model key
    def generate_fn(prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        model_answer = generate(model, tokenizer, messages)
        _, answer = split_function(model_answer)
        return answer
   
    for item in data:
        for response_data in item["generate_data"]:
            model_answer = response_data["final_answer"]
            correct_answer = item["answer"]
            prompt = construct_prompt(model_answer, correct_answer)
            model_key = "deepseek_r1_distill_qwen_14b"
            judge = JudgeMajority(generate_fn=generate_fn, max_retries=20)
            is_correct = judge.judge(prompt, K=k)
            response_data["is_correct_judged"] = is_correct
            #print for debug
            print(f"Model answer: {model_answer}")
            print(f"Is correct judged: {is_correct}")

        #save to the same path after processing all generate_data
        with open(path, "w") as f:
            json.dump(data, f, indent=4)





            


