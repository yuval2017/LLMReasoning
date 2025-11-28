import os
from config import init_config

# init configurations
config = init_config()
print("Initializing environment...")
config.init_env()
print("Environment initialized.")

from models_factory import get_default_system_prompt, get_model_and_split_function
from utils import load_model, generate, generate_with_time
import torch
import json
from json_pipeline import JsonPipeline


#params
prompt_row_name = "question" 
general_sys_prompt = None


def num_of_tokens(text, tokenizer):
    return len(tokenizer.tokenize(text, add_special_tokens=False))

def gen_function(data, model, tokeniezer, split_function):
    prompt = data[prompt_row_name]
    messages = [
        {"role": "system", "content": general_sys_prompt},
        {"role": "user", "content": prompt},
    ]
    answer, total_time = generate_with_time(model, tokeniezer, messages)
    think, final_answer = split_function(answer)
    num_of_think_tokens = num_of_tokens(think, tokeniezer)
    num_of_answer_tokens = "N/A"
    if final_answer is not None:
        num_of_answer_tokens = num_of_tokens(final_answer, tokeniezer)
    ret_val =  {
        "think": think.strip() if think is not None else None,
        "final_answer": final_answer.strip() if final_answer is not None else None,
        "num_of_think_tokens": num_of_think_tokens,
        "num_of_answer_tokens": num_of_answer_tokens,
        "generation_time": total_time,
    }
    #print(ret_val)
    for key, value in ret_val.items():
        print(f"{key}: {value}")
    print("--" * 50)
    return ret_val
# main execution
if __name__ == "__main__":
    #check for cuda
    if not torch.cuda.is_available():
        raise EnvironmentError("CUDA is not available. Please check your CUDA installation.")
    gpu_id = 0  # default GPU id
    #model_key = "microsoft_phi-4_Plus"
    #model_key = "deepseek_r1_distill_qwen_7b"
    model_key = "deepseek_r1_distill_qwen_14b"
    #model_key = "microsoft_phi-4_mini_flash"
    # load models from data folder
    model_name, split_function = get_model_and_split_function(model_key)    
    general_sys_prompt = get_default_system_prompt(model_name)
    model_kwargs = {
        "dtype": torch.float16,
        "trust_remote_code": True,
        "use_cache": False,
    }
    tokenizer_kwargs = {}
    kwargs = {"model_kwargs": model_kwargs, "tokenizer_kwargs": tokenizer_kwargs}
    model, tokenizer = load_model(model_name, device_map=f"cuda:{gpu_id}", **kwargs)
    # Check the device of the model parameters
    device = next(model.parameters()).device
    print("Model device:", device)
    #check for a dir with model key

    if not os.path.exists(f"result/{model_key}"):
        os.makedirs(f"result/{model_key}")
    data_path = "data/asdiv_evaluation_format.json"
    out_path = f"result/{model_key}/asdiv_evaluation_format.json"
    #out_path = "result/asdiv_phi4_plus_results.json"
    k = 5
    json_pipeline = JsonPipeline(
        generate_func=lambda data: gen_function(data, model, tokenizer, split_function),
        k=k,
        data_path=data_path,
        out_path=out_path,
    )
    json_pipeline.evaluate()
    print("Evaluation complete.")
    