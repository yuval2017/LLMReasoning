import os
import psutil
from pydantic_settings import BaseSettings, SettingsConfigDict

class init_config(BaseSettings):
    hf_home: str
    hf_token: str
    cuda_launch_blocking: str
    torch_use_cuda_dsa: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra env vars not defined in the class
    )

    def init_env(self):
        """Apply the configuration to environment variables."""
        os.environ["HF_HOME"] = self.hf_home
        os.environ["HF_TOKEN"] = self.hf_token
        os.environ["CUDA_LAUNCH_BLOCKING"] = self.cuda_launch_blocking
        os.environ["TORCH_USE_CUDA_DSA"] = self.torch_use_cuda_dsa

    def clear_processes(self):
        # Get the current process ID
        current_pid = os.getpid()

        # Iterate over all running processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Skip the current Python process
                if proc.info['name'] == 'python' and proc.info['pid'] != current_pid:
                    proc.kill()
                    print(f"Killed process {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
