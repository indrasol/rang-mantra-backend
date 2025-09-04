import os
from dotenv import load_dotenv
from pathlib import Path

# First get the environment from ENV variable or default to 'development'
ENV = os.getenv('ENV', 'development')

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load the appropriate .env file based on environment
def load_env_file():
    # First try to load .env.{ENV} file
    env_file = BASE_DIR / f".env.{ENV}"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        # Force override existing environment variables
        load_dotenv(dotenv_path=env_file, override=True)
        return True
    
    # Fallback to the standard .env file
    default_env_file = BASE_DIR / ".env"
    if default_env_file.exists():
        print(f"Loading environment from {default_env_file}")
        # Force override existing environment variables
        load_dotenv(dotenv_path=default_env_file, override=True)
        return True
    
    # If no env file found
    print(f"Warning: No .env.{ENV} or .env file found")
    return False

# Load environment variables
load_env_file()

# Print environment for debugging
print(f"Running in {ENV} environment")


# Main

# Supabase configuration
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_URL_RM")
print(f"SUPABASE_PROJECT_URL: {SUPABASE_PROJECT_URL}")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY_RM")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY_RM")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY_RM")

# Google AI API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")