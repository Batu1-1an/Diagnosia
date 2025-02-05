import os
from database import get_db
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    # Get database connection
    supabase = get_db()
    
    # List of migration files in order
    migrations = [
        'setup_rls.sql'  # Only run the RLS changes for now
    ]
    
    try:
        for migration in migrations:
            print(f"Running migration: {migration}")
            
            # Read migration file
            with open(f"migrations/{migration}", 'r') as file:
                sql = file.read()
                
            # Execute migration using Supabase client
            result = supabase.rpc('exec_sql', {'query': sql}).execute()
            
            if hasattr(result, 'error') and result.error is not None:
                raise Exception(f"Migration failed: {result.error}")
                
            print(f"Migration {migration} completed successfully")
            
    except Exception as e:
        print(f"Error running migrations: {str(e)}")
        raise e

if __name__ == "__main__":
    run_migrations() 