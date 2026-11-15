#!/usr/bin/env python3
"""Fail closed on malformed public routing, unsupported identity or missing source assets."""
from pathlib import Path
from urllib.parse import urlsplit
from html.parser import HTMLParser
import re
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"index.html","services.html","resilience.html","security-operations.html","post-quantum.html","approach.html","research.html","evidence.html","about.html","engage.html","privacy.html","terms.html","capability-statement.html","404.html"}
class Audit(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.tags=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ('a','link','script','img'):self.refs.append(d.get('href') or d.get('src') or '')
  if t in ('main','section','div'):self.tags.append(t)
 def handle_endtag(self,t):
  if t in ('main','section','div'):
   if not self.tags or self.tags[-1]!=t:raise ValueError("invalid section nesting")
   self.tags.pop()
def main():
 pages=set(p.name for p in ROOT.glob("*.html"))
 assert pages==EXPECTED,(pages^EXPECTED)
 for f in ROOT.glob("*.html"):
  s=f.read_text(encoding="utf-8");a=Audit();a.feed(s)
  assert not a.tags,f"unclosed markup {f.name}"
  assert 'rel="canonical"' in s and 'name="description"' in s,f"missing metadata {f.name}"
  assert 'href="/engage.html"' in s or f.name=="engage.html",f"missing CTA {f.name}"
  assert "assets/img/headshot.jpg" not in s and '"@type": "Person"' not in s,f"misleading identity {f.name}"
  for u in a.refs:
   p=urlsplit(u)
   if p.scheme or p.netloc or not p.path or p.path=='/':continue
   assert (ROOT/p.path.lstrip('/')).is_file(),(f.name,u)
 for b in ["assets/site.css","assets/site.js","assets/favicon.svg","assets/og-card.svg","robots.txt","sitemap.xml"]:
  assert (ROOT/b).is_file(),b
 readme=(ROOT/"README.md").read_text()
 assert "pqexpert.io" in readme and "Cloudflare" in readme and "Proton" in readme
 s=(ROOT/"index.html").read_text()
 for v in ["Security engineering for decisions that matter","Engineering trust. Demonstrating resilience.","Restoration Security Consultants"]:
  assert v in s,v
 engage=(ROOT/"engage.html").read_text()
 assert "z3HWJ4Zx58oSRGaBNGe8" in engage
 assert "utm_source=restoration_mt_site" in engage
 assert "fake testimonials" not in engage.lower()
 print("PASS: 14 HTML pages, links, form attribution, separation, claims guardrails")
if __name__=="__main__":main()
