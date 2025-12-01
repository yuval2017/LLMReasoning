from utils import extract_think_and_after_deepseek, extract_think_and_after
models = {"reasoning_models":
    {
        "microsoft_phi-4_Plus": "microsoft/Phi-4-reasoning-plus",
        "microsoft_phi-4_mini-reasoning": "microsoft/Phi-4-mini-reasoning",
        "microsoft_phi-4-reasoning": "microsoft/Phi-4-reasoning",
        "deepseek_r1_distill_qwen_7b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "deepseek_r1_distill_qwen_14b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"  
    }
}
models_to_split_fruncions = [
    ({"microsoft/Phi-4-reasoning-plus",
      "microsoft/Phi-4-mini-reasoning",
      "microsoft/Phi-4-reasoning"},
      extract_think_and_after),
    ({"deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
      "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"},
      extract_think_and_after_deepseek)
]
defult_system_promtpts = [
    ({"microsoft/Phi-4-reasoning-plus",
      "microsoft/Phi-4-mini-reasoning",
      "microsoft/Phi-4-reasoning"},
"You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. Please structure your response into two main sections: Thought and Solution using the specified format: <think> {Thought section} </think> {Solution section}. In the Thought section, detail your reasoning process in steps. Each step should include detailed considerations such as analysing questions, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present the final solution that you deem correct. The Solution section should be logical, accurate, and concise and detail necessary steps needed to reach the conclusion. Now, try to solve the following question through the above guidelines:"),
    ({"deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
      "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"},
         "You are DeepSeek-R1, a helpful assistant. Write chain-of-thought inside <think> tags, and the final answer ONLY after </think>.")
]

def get_model(model_key: str):
    model_name = models["reasoning_models"].get(model_key)
    if not model_name:
        raise ValueError(f"Model key '{model_key}' not found in models.")
    return model_name

def get_split_function(model_name: str):
    for model_names, split_function in models_to_split_fruncions:
        if model_name in model_names:
            return split_function
    raise ValueError(f"No split function found for model '{model_name}'.")

def get_model_and_split_function(model_key: str):
    model_name = get_model(model_key)
    split_function = get_split_function(model_name)
    return model_name, split_function

def get_default_system_prompt(model_name: str):
    for model_names, sys_prompt in defult_system_promtpts:
        if model_name in model_names:
            return sys_prompt
    raise ValueError(f"No default system prompt found for model '{model_name}'.")