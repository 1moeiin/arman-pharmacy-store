from apps.catalog.sitemaps import CategorySitemap, ProductSitemap
from apps.core.sitemaps import StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
    "categories": CategorySitemap,
}
