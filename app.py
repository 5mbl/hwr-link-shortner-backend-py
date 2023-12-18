from dotenv import load_dotenv
from supabase_py import create_client, Client
from flask import Flask, request, redirect, jsonify
from flask_cors import CORS

import os

# Stellen Sie sicher, dass Sie die richtigen Pfade und Origin-Domains angeben.
app = Flask(__name__)
# CORS(app, resources={r"/shorten_url": {"origins": "http://localhost:3000"}})


load_dotenv()


# Init DB
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

rows = supabase.table('links').select().execute()


@app.route('/')
def welcomScreen():
    print("staaaaart")
    print(rows)
    return "This is our HWR Link Shortner API - Welcome"


# SHORT URL WITH AN ID AND PUSH IT TO OUR DATABASE
@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    # Ihre URL-Verkürzungslogik hier
    original_url = request.form['url']
    insert_data = {
        "original_url": original_url,
    }
    # daten in die db schicken
    response = supabase.table('links').insert(insert_data).execute()
    # Fetch the unique primary key from the insert response
    primary_key_id = response['data'][0]['id']
    # Use the primary_key_id as the short_id
    short_id = str(primary_key_id)

    print("Supabase Response:", response)  # This is for debugging

    if 'data' in response and response['data']:
        return jsonify({"message": f"Your shortened URL has been successfully shortened. shortID: {short_id}"})
    else:
        return jsonify({"message": "Failed to shorten the URL"}), 400


# RETURN ONLY DATA (OUR JOB AS AN API)
@app.route('/get/<short_id>', methods=['GET'])
def get_originial_url(short_id):
    # Fetch original_url from Supabase
    fetched_data = supabase.table('links').select(
        'original_url').eq('id', short_id).execute()

    # print("fetched data: ", fetched_data) # This is for debugging
    original_url = fetched_data['data'][0]['original_url']
    # print(original_url) # This is for debugging

    if original_url:
        return jsonify({"data": f"{original_url}"})
    else:
        return jsonify({"message": "URL not found"}), 400


# REDIRECT SERVICE
@app.route('/<short_id>', methods=['GET'])
def redirect_to_original_url(short_id):
    try:
        # Fetch original_url and click_count from Supabase
        fetched_data = supabase.table('links').select(
            'original_url').eq('id', short_id).execute()

        if fetched_data['data']:
            original_url = fetched_data['data'][0].get('original_url')
            # Redirect to the original URL
            if original_url:
                if original_url.startswith("http://") or original_url.startswith("https://"):
                    return redirect(original_url)
                else:
                    return redirect("https://" + original_url)
            else:
                return 'URL not found', 404
        else:
            return 'URL not found', 404
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return 'Internal Server Error', 500
