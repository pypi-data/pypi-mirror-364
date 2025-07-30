import random
import string
from lexrchainer_client.client_interface import ClientInterface
from lexrchainer_client.models import WebhookCreate, WebhookType, GenericWebhookRequest
import os
from dotenv import load_dotenv

def random_joke():
    jokes = [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the bicycle fall over? Because it was two-tired!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the math book look sad? Because it had too many problems!"
    ]
    return random.choice(jokes)

def setup_client():
    # Set API key for authentication
    os.environ["LEXRCHAINER_API_KEY"] = "BpXlQI4iLYNI95KLKi9oPhWyVTZbfTHf-fUQ95duJGI"
    # Optionally set API URL if needed, e.g.:
    os.environ["LEXRCHAINER_API_URL"] = "http://localhost:8000"
    #os.environ["LEXRCHAINER_API_URL"] = "http://lexr-api-lb-492309865.us-east-1.elb.amazonaws.com"
    os.environ["LEXRCHAINER_API_KEY"] = "master-test-api-key"
    load_dotenv()
    return ClientInterface()

def create_webhook():
    client = setup_client()
    webhook_name = "test_webhook_" + ''.join(random.choices(string.ascii_lowercase, k=6))
    webhook = WebhookCreate(
        name=webhook_name,
        webhook_type=WebhookType.GENERIC,
        description="Test webhook for API call",
        metadata={"purpose": "test"}
    )
    webhook_response = client.create_webhook(webhook)
    print("Created webhook ID:", webhook_response.id)
    print("Webhook auth token:", webhook_response.auth_token)
    return webhook_response

def call_webhook(id, auth_token, request_id):
    client = setup_client()
    joke = random_joke()
    joke_data = {"joke": joke}
    generic_request = GenericWebhookRequest(data=joke_data, request_id=request_id)
    result = client.call_generic_webhook_handler(
        webhook_id=id,
        request=generic_request,
        auth_token=auth_token
    )
    print("Webhook call result:", result)

# Example usage:
#webhook_resp = create_webhook()
call_webhook("170c0e0b-de2e-4d1d-99c0-d57cfb0a17b7", "wh_EWwMONcZX-tZTfmqFzrZ9VinJz3G4sfQVu4reYEHmdI", "2f8d1d11-08a3-4c16-bb05-24c84c0160bc")
