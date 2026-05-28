import os


AUTH_TIMEOUT_SECONDS = int(os.getenv("AUTH_TIMEOUT_SECONDS", "4"))


def refresh_token(client):
    return client.refresh(timeout=AUTH_TIMEOUT_SECONDS)

