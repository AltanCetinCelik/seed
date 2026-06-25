import json, re, urllib.request, shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from html.parser import HTMLParser
STATE_FILE=Path("seed_browser_use_adapter_v68.json")
class P(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            href=dict(attrs).get("href")
            if href: self.links.append(href)
    def handle_data(self,data):
        if data and data.strip(): self.text.append(data.strip())
def browser_use_available():
    try: __import__("browser_use"); return True
    except Exception: return False
def read_page(url,max_bytes=500000):
    p=urlparse(url)
    if p.scheme not in {"http","https"} or not p.netloc: return {"ok":False,"error":"Invalid URL"}
    req=urllib.request.Request(url,headers={"User-Agent":"SeedBrowserReadOnly/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r: html=r.read(max_bytes).decode("utf-8",errors="ignore"); ct=r.headers.get("content-type","")
    parser=P(); parser.feed(html); text=re.sub(r"\s+"," "," ".join(parser.text)).strip(); data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"url":url,"mode":"read_only","browser_use_installed":browser_use_available(),"content_type":ct,"summary":text[:1600],"links":parser.links[:40],"dry_run_actions":["summarize page","extract links","no click without approval","no login/form/purchase"]}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_browser_use_status(): print(json.dumps({"ok":True,"browser_use_installed":browser_use_available(),"playwright":bool(shutil.which("playwright")),"mode":"read-only adapter active"},indent=4))
def show_browser_use_read(): print(json.dumps(read_page(input("URL: ").strip()),indent=4))
if __name__=="__main__": show_browser_use_status()
