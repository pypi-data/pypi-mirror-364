import requests
from thorcast_api_client.auth import AuthManager
from thorcast_api_client.config import API_BASE_URL
from thorcast_api_client.exceptions import APIClientError, AuthenticationError, RateLimitExceeded, ServerError

class ThorCastClient:
    """Client pour interagir avec l'API ThorCast."""
    
    def __init__(self, username: str, password: str):
        self.auth = AuthManager(username, password)
        self.auth.authenticate()

    def _request(self, method: str, endpoint: str, **kwargs):
        """Méthode générique pour effectuer une requête."""
        url = f"{API_BASE_URL}{endpoint}"
        headers = self.auth.get_headers()

        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise AuthenticationError(401, "Echec d'authentification, token invalide.")
        elif response.status_code == 429:
            raise RateLimitExceeded(429, "Limite de requêtes dépassée.")
        elif response.status_code >= 500:
            raise ServerError(response.status_code, "Erreur interne du serveur.")
        elif not response.ok:
            raise APIClientError(response.status_code, "Erreur inconnue.")

        return response.json()

    def get_lt_curves_versions(self, prms: list):
        """Liste les versions disponibles des courbes de charge LT."""
        endpoint = f"/backend/thorcast/v1/lt_curves/versions/?prms={','.join(prms)}"
        return self._request("GET", endpoint)

    def get_lt_curves(self, prms: list, sd: str, ed: str, versions: list = None, tz: str = "UTC"):
        """Récupère les courbes de charge LT."""
        endpoint = f"/backend/thorcast/v1/lt_curves/?prms={','.join(prms)}&sd={sd}&ed={ed}&tz={tz}"
        if versions:
            endpoint += f"&versions={','.join(versions)}"
        return self._request("GET", endpoint)
    
    def get_historical_curves(self, prms: list, sd: str, ed: str, tz: str = "UTC"):
        """Récupère les courbes de charge historiques."""
        endpoint = f"/backend/thorcast/v1/historical_load_curves/?prms={','.join(prms)}&sd={sd}&ed={ed}&tz={tz}"
        return self._request("GET", endpoint)
    
    def get_catalog_versions(self, catalogs: list, sd: str, ed: str):
        """Liste les versions disponibles des courbes de charge LT."""
        endpoint = f"/backend/thorcast/v1/catalog_curves/versions/?catalogs={','.join(catalogs)}&sd={sd}&ed={ed}"
        return self._request("GET", endpoint)
    
    def get_catalog_curves(self, ids: list, tz: str = "UTC"):
        """Récupère les courbes de charge catalog."""
        endpoint = f"/backend/thorcast/v1/catalog_curves/?ids={','.join(ids)}&tz={tz}"
        return self._request("GET", endpoint)