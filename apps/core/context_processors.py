from django.conf import settings

from .models import SiteSetting


def site_meta(request):
    """Site-wide values every template needs for <head> tags and the layout."""
    site_settings = SiteSetting.load()
    scheme = getattr(settings, "SITE_SCHEME", "https")
    domain = getattr(settings, "SITE_DOMAIN", request.get_host())
    return {
        "site_settings": site_settings,
        "SITE_NAME": site_settings.site_name or settings.SITE_NAME,
        "SITE_BASE_URL": f"{scheme}://{domain}",
        "CANONICAL_URL": request.build_absolute_uri(request.path),
    }
