#!/usr/bin/python3
from app import create_app
from flask_cors import CORS

app = create_app()
# ✅ Allow only frontend on http://localhost:5500
CORS(app, resources={r"/*": {"origins": ["http://localhost:5500"]}}, supports_credentials=True)

app.config['PREFERRED_URL_SCHEME'] = 'http'

if __name__ == '__main__':
    app.run(debug=True)
