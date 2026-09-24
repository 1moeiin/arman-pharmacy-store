class SecurityHeadersMiddleware:
    """Small extra hardening headers not covered by SecurityMiddleware/CSP."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        return response
