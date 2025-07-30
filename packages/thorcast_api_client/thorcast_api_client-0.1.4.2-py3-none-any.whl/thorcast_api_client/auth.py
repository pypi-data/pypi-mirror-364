import requests
from thorcast_api_client.config import API_BASE_URL

class AuthManager:
    """Gère l'authentification et le rafraîchissement du token JWT."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.token = None
        self.refresh_token = None

    def authenticate(self):
        """Récupère un token JWT"""
        url = f"{API_BASE_URL}/backend/auth/token/"
        payload = {"email": self.username, "password": self.password}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            self.token = data["access"]
            self.refresh_token = data["refresh"]
        else:
            raise Exception(f"Erreur d'authentification: {response.text}")

    def get_headers(self):
        """Retourne les headers avec le token d'accès"""
        if not self.token:
            raise Exception("Token non défini, veuillez vous authentifier.")
        return {"Authorization": f"Bearer {self.token}"}
