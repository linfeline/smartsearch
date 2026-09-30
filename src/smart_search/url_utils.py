import re
from urllib.parse import urlsplit


_URL_PATTERN = re.compile(r'(?<![A-Za-z0-9+.\-])https?://[^\s<>"\'`]+', re.IGNORECASE)
_URL_TRAILING_PUNCTUATION = ".,;:!?，。；：！？、…．*"
_URL_BRACKET_PAIRS = (
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("（", "）"),
    ("【", "】"),
    ("《", "》"),
    ("〈", "〉"),
    ("「", "」"),
    ("『", "』"),
)
_URL_TEXT_BOUNDARIES = ("（", "【", "《", "〈", "「", "『")


def normalize_extracted_url(value: str) -> str:
    url = (value or "").strip()
    if not url:
        return ""

    markdown_boundary = url.find("](")
    if markdown_boundary >= 0:
        url = url[:markdown_boundary]
    emphasis_boundary = url.find("**")
    if emphasis_boundary >= 0:
        url = url[:emphasis_boundary]
    for boundary in _URL_TEXT_BOUNDARIES:
        index = url.find(boundary)
        if index >= 0:
            url = url[:index]

    while url:
        candidate = url.rstrip(_URL_TRAILING_PUNCTUATION)
        for opening, closing in _URL_BRACKET_PAIRS:
            while candidate.endswith(closing) and candidate.count(closing) > candidate.count(opening):
                candidate = candidate[:-1]
        if candidate == url:
            break
        url = candidate

    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError:
        return ""
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.netloc
        or not hostname
        or any(char.isspace() for char in url)
        or "\\" in url
    ):
        return ""
    scheme, separator, remainder = url.partition(":")
    return f"{scheme.lower()}{separator}{remainder}"


def extract_unique_urls(text: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for match in _URL_PATTERN.finditer(text or ""):
        url = normalize_extracted_url(match.group())
        if not url or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls
