#srun --jobid=7405660 --pty bash
import os
if __name__ == "__main__":
    job_id = 7614521
    expressions = ["(8 / 4)", "(5 + 4)"]
    ssh_command = f"srun --jobid={job_id} --pty bash"
    go_dir_command = "cd /home/hitter/LLMReasoning"
    conda_command = "conda activate py312"
    py_file_path = "/home/hitter/LLMReasoning/pipline.py"
    log_file_dir = "/home/hitter/LLMReasoning/logs"
    
    
    commands = []
    for cuda_num, expression in enumerate(expressions):
        log_file_path = f"{log_file_dir}/pipeline_{job_id}_{cuda_num}.log"
        command = f"nohup python3 -u {py_file_path} {cuda_num} '{expression}' > {log_file_path} 2>&1 &"
        commands.append(command)
    
    ##create full commands    
    print("# Commands to run:")
    print(go_dir_command)
    print(ssh_command)
    print(conda_command)
    for cmd in commands:
        print(f"Executing command: {cmd}")
        #os.system(cmd)
