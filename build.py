#!/usr/bin/env python3
"""Bouwt de website van EAC De Sperwers naar de map public/.

Gebruik:  pip install -r requirements.txt  &&  python build.py
Inhoud staat in content/ (Markdown), instellingen in data/ (YAML),
opmaak in templates/ en vaste bestanden (css, js, foto's, pdf's) in src/.
"""
import datetime as dt
import html
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
OUT = ROOT / "public"
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]

env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                  autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)


def load_yaml(name):
    return yaml.safe_load((ROOT / "data" / name).read_text(encoding="utf-8")) or {}


def read_md(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    return meta, body.strip()


def as_date(value):
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value)[:10])


def date_fields(d):
    return {"date_iso": d.isoformat(), "day": d.day, "month_short": MAANDEN[d.month - 1][:3],
            "year": d.year, "date_long": f"{d.day} {MAANDEN[d.month - 1]} {d.year}"}


def md_to_html(body):
    out = markdown.markdown(body, extensions=["tables", "md_in_html", "sane_lists", "attr_list"])
    out = re.sub(r"<table>", '<div class="table-scroll"><table>', out)
    return out.replace("</table>", "</table></div>")


def first_image(body):
    m = re.search(r"!\[[^\]]*\]\(([^)\s]+)", body) or re.search(r'<img[^>]+src="([^"]+)"', body)
    return m.group(1) if m else None


def summary(body, n=150):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)|<[^>]+>|[*#_>`]|\[([^\]]*)\]\([^)]*\)", r"\1", body)
    text = " ".join(line.strip() for line in text.splitlines() if line.strip())
    text = re.sub(r"^\d{1,2} \w+ \d{4} – \d{1,2} \w+ \d{4}\s*", "", text)
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def write(url, page_html):
    target = OUT / url.strip("/") / "index.html" if not url.endswith(".html") else OUT / url.strip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page_html, encoding="utf-8")


def build():
    today = dt.date.today()
    site = load_yaml("site.yml")
    menu = load_yaml("menu.yml")
    sponsors = load_yaml("sponsors.yml")
    common = {"site": site, "menu": menu, "sponsors": sponsors, "year": today.year,
              "build_id": dt.datetime.now().strftime("%Y%m%d%H%M")}
    forms = env.get_template("forms.html").module

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "src", OUT)
    urls = []

    # menu-index: url -> (titel, ouder) voor kruimelpad en subpagina-kaarten
    parents, children = {}, {}
    for item in menu:
        for s in item.get("sub", []) or []:
            parents[s["url"]] = item
            children.setdefault(item["url"], []).append(s)

    # Pagina's
    for path in sorted((ROOT / "content" / "pages").glob("*.md")):
        meta, body = read_md(path)
        url = meta["permalink"]
        content = md_to_html(body)

        def subpaginas(_m, url=url):
            items = children.get(url, [])
            if not items:
                prefix = url
                items = [{"titel": m["title"], "url": m["permalink"]} for m in all_pages
                         if m["permalink"] != url and m["permalink"].startswith(prefix)
                         and m["permalink"].count("/") == url.count("/") + 1]
            links = "".join(f'<li><a href="{html.escape(i["url"])}"' +
                            (' target="_blank" rel="noopener"' if i["url"].startswith("http") else "") +
                            f'>{html.escape(i["titel"])}</a></li>' for i in items)
            return f'<ul class="subpages">{links}</ul>'

        content = re.sub(r"<p>\[\[subpaginas\]\]</p>", subpaginas, content)
        content = re.sub(r"<p>\[\[formulier:([a-z-]+)\]\]</p>", lambda m: forms.form(m.group(1), site), content)
        if meta.get("pdf"):
            pdf = html.escape(meta["pdf"])
            content = content.replace("<p>[[pdf]]</p>",
                f'<p><a class="btn btn-outline" href="{pdf}" download>Download PDF</a></p>'
                f'<object class="pdf-view" data="{pdf}" type="application/pdf"><p><a href="{pdf}">Open de PDF</a></p></object>')
        crumbs = []
        parent = parents.get(url)
        if not parent:
            parent_url = url.rstrip("/").rsplit("/", 1)[0] + "/"
            parent = next((m for m in menu if m["url"] == parent_url), None) if parent_url != "/" else None
        if parent:
            crumbs.append({"titel": parent["titel"], "url": parent["url"]})
        page = env.get_template("page.html").render(**common, title=meta["title"], url=url,
                                                    content=content, crumbs=crumbs, hero=meta.get("hero"))
        write(url, page)
        urls.append(url)

    # Nieuws
    posts = []
    for path in (ROOT / "content" / "nieuws").glob("*.md"):
        meta, body = read_md(path)
        d = as_date(meta["date"])
        slug = meta.get("slug") or path.stem
        post = {"title": meta["title"], "url": f"/nieuws/{slug}/", "kind": "nieuws", **date_fields(d),
                "afbeelding": meta.get("afbeelding") or first_image(body),
                "samenvatting": meta.get("samenvatting") or summary(body), "date": d,
                "content": md_to_html(body)}
        posts.append(post)
    posts.sort(key=lambda p: p["date"], reverse=True)
    for p in posts:
        write(p["url"], env.get_template("post.html").render({**p, **common, "url": p["url"]}))
        urls.append(p["url"])
    write("/nieuws/", env.get_template("nieuws.html").render(**common, title="Nieuws", url="/nieuws/", posts=posts))
    urls.append("/nieuws/")

    # Agenda
    events = []
    for path in (ROOT / "content" / "agenda").glob("*.md"):
        meta, body = read_md(path)
        d = as_date(meta["date"])
        events.append({**meta, "title": meta["title"], "kind": "agenda", "date": d, **date_fields(d),
                       "content": md_to_html(body) if body else "",
                       "url": meta.get("informatie") or meta.get("inschrijven") or "/agenda/"})
    events.sort(key=lambda e: e["date"])
    upcoming = [e for e in events if e["date"] >= today]
    past = [e for e in events if e["date"] < today][::-1]
    write("/agenda/", env.get_template("agenda.html").render(**common, title="Agenda", url="/agenda/",
                                                             upcoming=upcoming, past=past))
    urls.append("/agenda/")

    # Home: carrousel met komende uitgelichte activiteiten en het laatste nieuws
    highlights = [e for e in upcoming if e.get("uitgelicht", True)][:8] + posts[:3]
    write("/", env.get_template("home.html").render(**common, title=site["naam"], url="/", highlights=highlights))
    urls.insert(0, "/")

    write("404.html", env.get_template("404.html").render(**common, title="Pagina niet gevonden", url="/404"))

    # Sitemap
    sm = "".join(f"<url><loc>{site['url']}{u}</loc></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin/\nSitemap: {site['url']}/sitemap.xml\n", encoding="utf-8")
    print(f"Klaar: {len(urls)} pagina's, {len(upcoming)} komende activiteiten, {len(posts)} nieuwsberichten → {OUT}")


all_pages = [read_md(p)[0] for p in sorted((ROOT / "content" / "pages").glob("*.md"))]

if __name__ == "__main__":
    build()
