from builtins import ValueError
from functools import wraps
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import time
def format_args(**kwargs):
    return "\n".join(f"{key}={value}" for key, value in kwargs.items())
    
def load_model(model_name, device_map="auto", **kwargs):
    model_kwargs = kwargs.get("model_kwargs", {})
    tokenizer_kwargs = kwargs.get("tokenizer_kwargs", {})
    print(f"model_kwargs:\n{format_args(**model_kwargs)}\n{25*"-"}\ntokenizer_kwargs:\n{format_args(**tokenizer_kwargs)}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, **tokenizer_kwargs)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map, **model_kwargs)

    #if the model is llama add the special tokens
    if "llama" in model_name.lower():
        pad_token = "<pad>"
        tokenizer.add_special_tokens({'pad_token': pad_token})
        tokenizer.pad_token = pad_token
        # Resize the model embeddings to match the new tokenizer size
        model.resize_token_embeddings(len(tokenizer), mean_resizing=False)
        pad_token = pad_token

        print(f"Added special token {pad_token} to the tokenizer")
        print(tokenizer.pad_token)
        print(tokenizer.pad_token_id)
        tokenizer.padding_side = 'left'
        
    return model, tokenizer

def generate(model, tokenizer, messages, **generate_kwargs):
    # 1) Build prompt text using ChatML template
    prompt_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # 2) Tokenize — ALWAYS produces both input_ids + attention_mask
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        padding=False,
        truncation=False
    ).to(model.device)

    input_ids = encoded["input_ids"]
    attention_mask = encoded["attention_mask"]

    # Dynamic max: allow model to generate up to FULL context window
    max_new_tokens = model.config.max_position_embeddings - input_ids.shape[1]
    if max_new_tokens < 1:
        raise ValueError("Input is too long for the model's context window.")

    # 3) Generate
    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        temperature=0.8,
        top_k=50,
        top_p=0.95,
        pad_token_id=tokenizer.pad_token_id,
        do_sample=True,
        **generate_kwargs
    )

    # 4) Extract ONLY new tokens
    answer = tokenizer.decode(
        outputs[0][input_ids.shape[1]:],
        skip_special_tokens=True
    )

    return answer


def extract_think_and_after(text: str):
    match = re.search(r"<think>(.*?)</think>(.*)", text, re.DOTALL)
    if match:
        inside = match.group(1)   # content inside <think>
        after = match.group(2)    # everything after </think>
        return inside, after
    return text, None  # no <think> found → return None + whole text

def extract_think_and_after_deepseek(text: str):
    match = re.search(r"(.*?)</think>(.*)", text, re.DOTALL)
    if match:
        inside = match.group(1)   # content inside <think>
        after = match.group(2)    # everything after </think>
        return inside, after
    return text, None  # no <think> found → return None + whole text
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        total_time = end - start
        # print(f"{func.__name__} took {end - start:.4f} seconds")
        return result, total_time

    return wrapper


@timed
def generate_with_time(model, tokenizer, messages):
    answer = generate(model, tokenizer, messages)
    return answer

