class UnicodeSlugConverter:
    """Django's built-in `slug` converter is ASCII-only; our slugs are
    generated with allow_unicode=True so Persian product/category names get
    readable, SEO-friendly URLs instead of transliterated garbage."""

    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
