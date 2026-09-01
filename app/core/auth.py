from supabase import create_client
from app.config import SUPABASE_URL,SUPABASE_ANON_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def sign_up(email, password):
    return supabase.auth.sign_up({"email": email, "password" : password})

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_out():
    supabase.auth.sign_out()