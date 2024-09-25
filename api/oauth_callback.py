from flask import Flask, request, session
from google_auth_oauthlib.flow import Flow
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
        "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI")]
    }
}

@app.route('/api/oauth_callback')
def oauth_callback():
    state = session['state']

    flow = Flow.from_client_config(
        client_config=GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")

    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    # Here you would typically store these credentials and associate them with the user
    # For this example, we're just returning a success message
    return "Successfully logged in! You can now use the /scan command in your Telegram bot."

if __name__ == '__main__':
    app.run(debug=True)
