API_BASE_URL = "https://api.xyz.corp.lightboxre.com/v1/los"
TOKEN_URL = f"{API_BASE_URL}/oauth/token"
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
PROXY = "http://your-proxy-url:8080"
VERIFY_SSL = False
MAX_RETRIES = 3
BASE_DELAY = 1  # Start with 1 second delay

# Cache TTL (in seconds)
SCHEMA_CACHE_TTL = 900  # 15 minutes
SERVICE_TYPE_CACHE_TTL = 900  # 15 minutes