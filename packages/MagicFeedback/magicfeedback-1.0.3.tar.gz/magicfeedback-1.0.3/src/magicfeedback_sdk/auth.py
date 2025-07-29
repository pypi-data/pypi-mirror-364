import json
import time

import requests


class AuthManager:
    def __init__(self, ip_key: str, logger, user: str, password: str):
        self.ip_key = ip_key
        self.logger = logger
        self.user = user
        self.password = password

        self.id_token = None
        self.refresh_token = None
        self.token_expiry = 0  # tiempo UNIX en segundos

    def get_valid_token(self) -> str:
        if not self.id_token or time.time() >= self.token_expiry:
            if self.refresh_token:
                self.logger.info("Refreshing token...")
                self.refresh_id_token()
            else:
                self.logger.info("Logging in...")
                self.identity_login()
        return self.id_token

    def identity_login(self):
        self.logger.info("Logging in with user: %s", self.user)

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.ip_key}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "email": self.user,
            "password": self.password,
            "returnSecureToken": True
        })

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        self.id_token = data["idToken"]
        self.refresh_token = data["refreshToken"]
        self.token_expiry = time.time() + int(data["expiresIn"]) - 60  # margen de seguridad

    def refresh_id_token(self):
        url = f"https://securetoken.googleapis.com/v1/token?key={self.ip_key}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = f"grant_type=refresh_token&refresh_token={self.refresh_token}"

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()

        self.id_token = data["id_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expiry = time.time() + int(data["expires_in"]) - 60
