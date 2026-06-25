import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


BROWSER_FILE = Path("seed_browser_executor_v35.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def validate_url(url):
    p = urlparse(url)
    return p.scheme in {"http", "https"} and bool(p.netloc)


def strip_html(text):
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_readonly(url, max_bytes=300000):
    if not validate_url(url):
        return {"ok": False, "error": "Invalid URL.", "url": url}

    req = urllib.request.Request(url, headers={"User-Agent": "SeedReadOnlyBrowser/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        raw = response.read(max_bytes)
        content_type = response.headers.get("content-type", "")
        text = raw.decode("utf-8", errors="ignore")

    clean = strip_html(text)
    summary = clean[:1200]

    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "mode": "read_only",
        "url": url,
        "content_type": content_type,
        "chars": len(clean),
        "summary": summary,
        "blocked_actions": ["login", "forms", "purchase", "account_action", "download_execute"]
    }

    BROWSER_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_browser_readonly():
    url = input("URL: ").strip()
    print(json.dumps(fetch_readonly(url), indent=4))


if __name__ == "__main__":
    show_browser_readonly()
