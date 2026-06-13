#!/usr/bin/env python3
# /// script
# dependencies = ["requests", "beautifulsoup4", "requests-cache", "json5"]
# ///
import html
import re
import json
import json5
import time
import requests
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pathlib import Path

session = requests_cache.CachedSession(".cache/http", backend="filesystem")
session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=2, status_forcelist=[502, 503, 504])))

BASE = "https://www.bancaetica.it"
ARCHIVE = f"{BASE}/archivio-assemblee/"
DATA = Path("data")

MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}

def get_all_risultati_links():
    links = []
    page = 1
    while True:
        url = ARCHIVE if page == 1 else f"{ARCHIVE}?paged={page}"
        r = session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        found = soup.find_all("a", string=re.compile(r"Risultati", re.I))
        if not found:
            break
        for a in found:
            href = a["href"]
            if not href.startswith("http"):
                href = BASE + href
            links.append(href)
        print(f"Page {page}: {len(found)} links")
        page += 1
        time.sleep(0.3)
    return links

def extract_braced(text, start):
    """Return the substring from text[start] (a '{') to its matching '}'."""
    depth, i = 0, start
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("Unmatched brace")

def extract_all_charts(text):
    charts = {}
    for m in re.finditer(r"const\s+myChartData\s*=\s*\{", text):
        block_start = m.end() - 1  # position of opening '{'
        # extract just type and data fields before parsing
        type_m = re.search(r"type:\s*'([^']+)'", text[block_start:block_start + 200])
        chart_type = type_m.group(1) if type_m else "unknown"

        data_m = re.search(r"\bdata:\s*\{", text[block_start:])
        if not data_m:
            continue
        data_start = block_start + data_m.start() + data_m.end() - data_m.start() - 1
        # find the '{' of data value
        brace_pos = text.index('{', block_start + data_m.start())
        raw_data = extract_braced(text, brace_pos)

        # find chart id that follows this block
        rest = text[block_start:]
        id_m = re.search(r"Chart\('([^']+)',\s*myChartData", rest)
        if not id_m:
            continue
        chart_id = id_m.group(1)

        charts[chart_id] = {"type": chart_type, "data": json5.loads(raw_data)}

        # advance past this block so next finditer picks up the next one
        # (re.finditer already advances, but we need the next const myChartData after this chart id)
        # handled naturally by finditer scanning forward
    return charts

ZONE_STAT_KEY = {
    "votanti": "votanti",
    "donne": "donne",
    "uomini": "uomini",
    "persone fisiche": "persone_fisiche",
    "persone giuridiche": "persone_giuridiche",
    "in presenza": "in_presenza",
    "a distanza": "a_distanza",
}

def extract_zones(soup):
    zones = {}
    for zone_div in soup.find_all(class_="meetings-results__zone"):
        name = html.unescape(zone_div.get_text(strip=True))
        container = zone_div.find_parent("div") or zone_div
        stats = {}
        for stat in container.find_all(class_="meetings-results__map-stats"):
            text = stat.get_text(strip=True)
            m = re.match(r"^(.+?):\s*(\d+)$", text)
            if m:
                key = ZONE_STAT_KEY.get(m.group(1).lower(), m.group(1).lower().replace(" ", "_"))
                stats[key] = int(m.group(2))
        if stats:
            zones[name] = stats
    return zones

def extract_province_table(soup):
    """Old format (2016): all data in one <tr>; flat list of cells in groups of 4 columns."""
    for table in soup.find_all("table"):
        full_text = table.get_text().lower()
        if "provincia" not in full_text or "totale" not in full_text:
            continue
        # collect all cells, skipping the giant merged summary cell (>200 chars)
        all_cells = [
            td.get_text(strip=True)
            for td in table.find_all(["th", "td"])
            if len(td.get_text(strip=True)) <= 200
        ]
        # find where the header starts
        start = next((i for i, c in enumerate(all_cells) if c.lower() == "provincia"), None)
        if start is None:
            continue
        headers = [c.lower() for c in all_cells[start:start + 4]]
        if not any("presenza" in h or "distanza" in h or "totale" in h for h in headers):
            continue
        idx_presenza = next((j for j, h in enumerate(headers) if "presenza" in h), None)
        idx_distanza = next((j for j, h in enumerate(headers) if "distanza" in h), None)
        idx_totale   = next((j for j, h in enumerate(headers) if "totale"   in h), None)
        provinces = {}
        data_cells = all_cells[start + 4:]
        for i in range(0, len(data_cells) - 3, 4):
            chunk = data_cells[i:i + 4]
            name = html.unescape(chunk[0])
            if not name or name.lower() == "provincia":
                continue
            def val(idx, chunk=chunk):
                if idx is not None and idx < len(chunk):
                    try:
                        return int(chunk[idx].replace(".", "").replace(",", ""))
                    except ValueError:
                        return None
                return None
            provinces[name] = {
                "in_presenza": val(idx_presenza),
                "a_distanza": val(idx_distanza),
                "totale": val(idx_totale),
            }
        if provinces:
            return provinces
    return {}

def extract_tables(soup):
    tables = []
    for table in soup.find_all("table"):
        rows = [
            [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
            for tr in table.find_all("tr")
        ]
        rows = [r for r in rows if any(c for c in r)]
        if rows:
            tables.append(rows)
    return tables

def parse_date(url, page_text):
    m = re.search(
        r"(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\w*\s+(\d{4})",
        page_text, re.I,
    )
    if m:
        return int(m.group(2)), MONTHS[m.group(1).lower()]
    # fallback: month from og:image upload path e.g. /uploads/2024/05/
    m2 = re.search(r"/uploads/(\d{4})/(\d{2})/", page_text)
    if m2:
        return int(m2.group(1)), int(m2.group(2))
    m3 = re.search(r"(\d{4})", url)
    if m3:
        return int(m3.group(1)), 0
    raise ValueError(f"Cannot extract date from {url}")

def main():
    DATA.mkdir(exist_ok=True)
    links = get_all_risultati_links()
    print(f"\nTotal: {len(links)} assemblee\n")
    for url in links:
        r = session.get(url)
        r.raise_for_status()
        year, month = parse_date(url, r.text)
        out = DATA / f"{year}.{month:02d}.json"
        if out.exists():
            print(f"  skip {out} (exists)")
            continue
        print(f"Fetching {url}")
        try:
            soup = BeautifulSoup(r.text, "html.parser")
            charts = extract_all_charts(r.text)
            zones = extract_zones(soup)
            if charts:
                data = charts
                if zones:
                    data["zones"] = zones
                print(f"  -> {out} ({len(charts)} charts, {len(zones)} zones)")
            else:
                tables = extract_tables(soup)
                data = {"tables": tables}
                provinces = extract_province_table(soup)
                if provinces:
                    data["zones"] = provinces
                elif zones:
                    data["zones"] = zones
                print(f"  -> {out} ({len(tables)} tables, {len(data.get('zones', {}))} zones)")
            out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
