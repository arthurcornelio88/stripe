import os
from dotenv import load_dotenv

def load_project_env(required_vars=None) -> str:
    ENV = os.getenv("ENV", "DEV").upper()
    env_file = f".env.{ENV.lower()}"

    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file)
        print(f"🔧 Loaded environment from {env_file}")
    else:
        raise RuntimeError(f"❌ Environment file '{env_file}' not found.")

    if required_vars:
        for key in required_vars:
            if not os.getenv(key):
                raise EnvironmentError(f"❌ Missing required env var: {key}")

    # Detect Supabase connection info (optional logging)
    host = os.getenv("POSTGRES_HOST", "")
    port = os.getenv("POSTGRES_PORT", "")

    if "supabase.com" in host:
        if "pooler" in host:
            print("🌐 Connected to Supabase (IPv4 Transaction Pooler)")
        elif host.startswith("db."):
            print("🌐 Connected to Supabase (IPv6 Direct DB)")

    return ENV
