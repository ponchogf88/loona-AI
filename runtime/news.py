"""Mexico / world headlines with images for the LOONA projection screen."""
from __future__ import annotations

import re
import time
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlparse

import httpx

_CACHE: dict = {}
_TTL = 180.0
FEEDS = [
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    "https://www.xataka.com/index.xml",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
]
AI_FEEDS = [
    "https://www.xataka.com/tag/inteligencia-artificial/rss2.xml",
    "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    "https://hipertextual.com/feed",
]
IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.I)
AI_RX = re.compile(
    r"\b(ia|ai|gpt|openai|gemini|claude|grok|llm|deepseek|anthropic|nvidia|"
    r"chatbot|inteligencia artificial|modelo de lenguaje)\b",
    re.I,
)
NS = {
    "media": "http://search.yahoo.com/mrss/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}
OG_RE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
OG_RE_REV = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.I,
)


def _text(el) -> str:
    if el is None or el.text is None:
        return ""
    return unescape(re.sub(r"<[^>]+>", "", el.text)).strip()


def _clean_img(url: str) -> str:
    url = unescape(url or "").strip()
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        return ""
    if "1x1" in url or url.endswith(".svg"):
        return ""
    return url


def _img_from_item(item) -> str:
    for tag in (
        "{http://search.yahoo.com/mrss/}content",
        "{http://search.yahoo.com/mrss/}thumbnail",
        "{http://search.yahoo.com/mrss/}thumbnail",
    ):
        node = item.find(tag)
        if node is not None:
            url = _clean_img(node.attrib.get("url") or node.attrib.get("href") or "")
            if url:
                return url
    enc = item.find("enclosure")
    if enc is not None:
        typ = enc.attrib.get("type") or ""
        url = _clean_img(enc.attrib.get("url") or "")
        if url and ("image" in typ or url.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))):
            return url
    blob = ""
    for tag in ("description", "{http://purl.org/rss/1.0/modules/content/}encoded"):
        node = item.find(tag)
        if node is not None and (node.text or node.itertext()):
            blob += " " + unescape("".join(node.itertext()) or (node.text or ""))
    found = IMG_RE.findall(blob)
    for cand in found:
        url = _clean_img(cand)
        if url:
            return url
    return ""


async def _og_image(client: httpx.AsyncClient, url: str) -> str:
    try:
        r = await client.get(url, follow_redirects=True, timeout=4.0)
        if r.status_code >= 400 or not r.text:
            return ""
        html = r.text[:80_000]
        m = OG_RE.search(html) or OG_RE_REV.search(html)
        return m.group(1) if m else ""
    except httpx.HTTPError:
        return ""


async def fetch_news(limit: int = 8, topic: str | None = None) -> list[dict]:
    now = time.time()
    key = topic or "general"
    cached = _CACHE.get(key)
    if cached and cached["items"] and now - cached["t"] < _TTL:
        return cached["items"][:limit]

    items: list[dict] = []
    feeds = AI_FEEDS if topic == "ai" else FEEDS
    async with httpx.AsyncClient(
        timeout=8.0,
        headers={"User-Agent": "LOONA/1.0 (personal OS; +local)"},
        follow_redirects=True,
    ) as client:
        for feed in feeds:
            try:
                resp = await client.get(feed)
                resp.raise_for_status()
                root = ET.fromstring(resp.content)
            except (httpx.HTTPError, ET.ParseError):
                continue
            channel = root.find("channel")
            nodes = channel.findall("item") if channel is not None else root.findall(".//item")
            for item in nodes:
                title = _text(item.find("title"))
                link = _text(item.find("link"))
                if not title or not link:
                    continue
                source_el = item.find("source")
                source = _text(source_el) or urlparse(link).netloc.replace("www.", "")
                img = _img_from_item(item)
                items.append(
                    {
                        "title": title,
                        "url": link,
                        "source": source,
                        "image": img,
                        "published": _text(item.find("pubDate")),
                    }
                )
            if len(items) >= 16:
                break

        # Enrich missing images (cap to keep the iMac snappy). Skip Google News shells.
        need = [
            it
            for it in items[:10]
            if not it["image"] and "news.google.com" not in (it.get("url") or "")
        ]
        for it in need[:6]:
            it["image"] = await _og_image(client, it["url"])

    # Prefer items that actually have a photo; AI topic also prefers keyword hits
    def _rank(it: dict) -> tuple:
        photo = 0 if it.get("image") else 1
        hit = 0 if topic != "ai" or AI_RX.search(it.get("title") or "") else 1
        return (photo, hit)

    items.sort(key=_rank)
    _CACHE[key] = {"t": now, "items": items[:12]}
    return _CACHE[key]["items"][:limit]
