from config import init_config

# init configurations
config = init_config()
print("Initializing environment...")
config.init_env()
print("Environment initialized.")

from utils import load_model, generate, extract_think_and_after, extract_think_and_after_deepseek, generate_with_time
from models_factory import get_model_and_split_function
import torch
model_name, split_function = get_model_and_split_function("microsoft_phi-4-reasoning")
#model_name = "microsoft/Phi-4-reasoning-plus"
gpu_id = 0  # default GPU id``
model_kwargs = {
    "dtype": torch.float16,
    "trust_remote_code": True,
    "use_cache": False,
}
tokenizer_kwargs = {}
kwargs = {"model_kwargs": model_kwargs, "tokenizer_kwargs": tokenizer_kwargs}
model, tokenizer = load_model(model_name, device_map=f"cuda:{gpu_id}", **kwargs)

messages = [
    {"role": "system", "content":
     "You are DeepSeek-R1, a helpful assistant. Write chain-of-thought inside <think> tags, and the final answer ONLY after </think>."},
    {"role": "user", "content": "Explain how gravity works."}
]
answer = generate(model, tokenizer, messages)
think, final_answer = split_function(answer)
print("Full answer:")
print(answer)
print("Think part:")
print(think)
print("Final answer:")
print(final_answer.strip())

