from supabase import create_client, Client
from dotenv import load_dotenv
import os
import urllib.parse
from flask import session, has_request_context

# Load environment variables
load_dotenv()

def init_supabase() -> Client:
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase URL or key in environment variables")

    # Clean and validate URL
    parsed_url = urllib.parse.urlparse(supabase_url)
    if not parsed_url.scheme:
        supabase_url = f"https://{supabase_url}"
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        raise

# Initialize the client
supabase = init_supabase()

def refresh_schema_cache(client: Client) -> None:
    try:
        client.postgrest.schema('public')
    except Exception as e:
        print(f"Error refreshing schema cache: {str(e)}")

def get_db() -> Client:
    # Only try to get session token if we're in a request context
    if has_request_context():
        access_token = session.get('access_token')
        if access_token:
            supabase.auth.set_session(access_token)
    
    # Force refresh schema cache
    refresh_schema_cache(supabase)
    return supabase 