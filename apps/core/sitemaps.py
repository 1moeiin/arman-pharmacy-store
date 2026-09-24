from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:about", "core:contact"]

    def location(self, item):
        return reverse(item)
