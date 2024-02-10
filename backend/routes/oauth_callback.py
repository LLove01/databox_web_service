from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional
from ..utilities.token_storage import access_tokens_storage
from ..components.oauth2 import exchange_code_for_token
import uuid
import os
import json

router = APIRouter()

google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

REDIRECT_URI = "http://localhost:8000/oauth-callback"


def generate_unique_identifier():
    return str(uuid.uuid4())


@router.get("/oauth-callback")
async def oauth_callback(code: Optional[str] = None):
    if code is None:
        return {"error": "Authorization code is missing"}
    try:
        # Exchange the authorization code for an access token
        token_response = await exchange_code_for_token(code, google_client_id, google_client_secret, REDIRECT_URI)
        if "access_token" in token_response:
            # Generate a unique identifier for the user
            user_identifier = generate_unique_identifier()
            # Store the access token associated with the user identifier
            access_tokens_storage[user_identifier] = token_response["access_token"]
            # Redirect the user back to the frontend with the user_id parameter
            frontend_url = f"http://localhost:3000/?user_id={user_identifier}"
            return RedirectResponse(url=frontend_url)
        else:
            return {"error": "Failed to fetch access token"}
    except Exception as e:
        return {"error": str(e)}
