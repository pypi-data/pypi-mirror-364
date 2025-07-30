class APIClientError(Exception):
    """Exception générique pour les erreurs API."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")

class AuthenticationError(APIClientError):
    """Erreur spécifique à l'authentification (ex: JWT expiré, mauvais identifiants)."""
    pass

class RateLimitExceeded(APIClientError):
    """Erreur lorsque la limite de requêtes est dépassée."""
    pass

class ServerError(APIClientError):
    """Erreur interne du serveur API."""
    pass
