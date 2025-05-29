# scripts/utils.py

import os
from dotenv import load_dotenv

def load_project_env():
    ENV = os.getenv("ENV", "DEV").upper()
    env_file = f".env.{ENV.lower()}"

    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
        print(f"🔧 Loaded environment from {env_file}")
    else:
        raise RuntimeError(f"❌ Environment file '{env_file}' not found.")

    return ENV
