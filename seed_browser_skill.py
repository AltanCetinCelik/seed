import re
import urllib.parse
import urllib.request
import webbrowser


try:
    from seed_config import SEED_BROWSER_READ_MAX_BYTES
except Exception:
    SEED_BROWSER_READ_MAX_BYTES = 150000


def normalize_url(url):
    url = (url or "").strip()
    if not url:
        raise ValueError("Empty URL.")

    if not re.match(r"^https?://", url):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        raise ValueError("Only valid http/https URLs are allowed.")

    return urllib.parse.urlunparse(parsed)


def open_url(url):
    safe_url = normalize_url(url)
    ok = bool(webbrowser.open(safe_url))
    return {
        "ok": ok,
        "verified": ok,
        "url": safe_url,
        "message": "Browser open requested." if ok else "Browser open failed."
    }


def strip_html(html):
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_url(url):
    safe_url = normalize_url(url)

    request = urllib.request.Request(
        safe_url,
        headers={"User-Agent": "SeedLocalSkill/2.5"}
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read(int(SEED_BROWSER_READ_MAX_BYTES))
        content_type = response.headers.get("Content-Type", "")
        final_url = response.geturl()

    raw = data.decode("utf-8", errors="ignore")
    text = strip_html(raw) if "html" in content_type.lower() else raw

    return {
        "ok": True,
        "url": safe_url,
        "final_url": final_url,
        "content_type": content_type,
        "bytes_read": len(data),
        "text": text[:12000],
        "truncated": len(data) >= int(SEED_BROWSER_READ_MAX_BYTES)
    }


def validate_url(url):
    try:
        safe_url = normalize_url(url)
        return {"ok": True, "url": safe_url}
    except Exception as error:
        return {"ok": False, "error": str(error), "url": url}


def run_browser_skill(operation, args=None):
    args = args or {}

    if operation == "open":
        return open_url(args.get("url", ""))

    if operation == "read":
        return read_url(args.get("url", ""))

    if operation == "validate":
        return validate_url(args.get("url", ""))

    return {"ok": False, "error": f"Unknown browser operation: {operation}"}


if __name__ == "__main__":
    print(validate_url("https://example.com"))
