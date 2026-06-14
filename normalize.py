#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
import html
import json
import re
import sys
from pathlib import Path

DATA = Path("data")
OUT = Path("normalized")

LABEL_KEY = {
    "votanti normali": "votanti_normali",
    "rappresentanze": "rappresentanze",
    "deleghe": "deleghe",
    "con delega": "deleghe",
    "a distanza": "a_distanza",
    "in presenza": "in_presenza",
    "persone fisiche": "persone_fisiche",
    "persone giuridiche": "persone_giuridiche",
    "uomini": "uomini",
    "donne": "donne",
    "italia": "italia",
    "spagna": "spagna",
    "estero": "estero",
}

def parse_number(s):
    s = str(s).strip().split()[0]  # first token — drops "(86,16%)" suffixes
    s = s.replace("\xa0", "").replace(" ", "")
    if "%" in s:
        s = s.replace("%", "").replace(",", ".")
        return float(s)
    return int(s.replace(".", "").replace(",", ""))

def safe_parse(s):
    try:
        return parse_number(s)
    except Exception:
        return None

# --- chart format (2023+) ---

def from_charts(data):
    def zip_chart(chart_id):
        c = data.get(chart_id)
        if not c:
            return {}
        labels = c["data"]["labels"]
        values = c["data"]["datasets"][0]["data"]
        return {LABEL_KEY.get(l.lower(), l.lower()): safe_parse(v) for l, v in zip(labels, values)}

    participants = zip_chart("chart-participants")
    mode = zip_chart("chart-mode")
    typology = zip_chart("chart-typology")
    genre = zip_chart("chart-genre")
    geography = zip_chart("chart-geographic-area")

    return build(participants, mode, typology, genre, geography)

# --- table format (2016-2022) ---

COUNTRIES = {"italia", "spagna", "estero"}

def table_text(rows):
    return " ".join(c for row in rows for c in row).lower()

def first_number(rows):
    for row in rows:
        for cell in row:
            v = safe_parse(cell)
            if v is not None:
                return v
    return None

def is_geo_subtable(rows):
    """Individual per-country table: single value with parenthetical % + 'Partecipanti'."""
    txt = table_text(rows)
    return "partecipanti" in txt and rows and rows[0] and "(" in rows[0][0]

def extract_label_value_rows(rows):
    """Tables where each row is [label, value, ...] or values row + labels row.
    Returns {canonical_key: value} driven purely by label text."""
    result = {}
    # Strategy A: label and value in the same row
    for row in rows:
        for i, cell in enumerate(row):
            key = LABEL_KEY.get(cell.strip().lower())
            if key:
                for c in row[i + 1:] + row[:i]:
                    v = safe_parse(c)
                    if v is not None:
                        result[key] = v
                        break
    # Strategy B: values row then labels row (e.g. mode, genre tables)
    # Find any row that consists entirely of labels we know
    for r_idx, row in enumerate(rows):
        label_row = [LABEL_KEY.get(c.strip().lower()) for c in row if c.strip()]
        label_row = [k for k in label_row if k]
        if len(label_row) >= 2:
            # collect numeric values from the preceding rows
            vals = []
            for prev in rows[:r_idx]:
                vals += [safe_parse(c) for c in prev if safe_parse(c) is not None]
            for key, val in zip(label_row, vals):
                if key not in result:
                    result[key] = val
    return result

def from_tables(tables):
    participants = {}
    mode = {}
    typology = {}
    genre = {}
    geography = {}
    geo_countries = []  # set when combined geo table is found

    for rows in tables:
        if not rows:
            continue

        # geography combined table: first row has 2+ country names
        header = [c.strip().lower() for c in rows[0]]
        countries_in_header = [c for c in header if c in COUNTRIES]
        if len(countries_in_header) >= 2:
            geo_countries = countries_in_header
            continue

        # geography individual sub-tables: follow the combined table in order
        if geo_countries and is_geo_subtable(rows):
            idx = len(geography)
            if idx < len(geo_countries):
                v = first_number(rows)
                if v is not None:
                    geography[geo_countries[idx]] = v
            continue

        txt = table_text(rows)

        if "deleghe" in txt or "con delega" in txt:
            participants["deleghe"] = first_number(rows)
        elif "rappresentanze" in txt:
            participants["rappresentanze"] = first_number(rows)
        elif "distanza" in txt or "presenza" in txt:
            mode.update(extract_label_value_rows(rows))
        elif "persone fisiche" in txt or "persone giuridiche" in txt:
            typology.update(extract_label_value_rows(rows))
        elif "donne" in txt or "uomini" in txt:
            genre.update(extract_label_value_rows(rows))
        elif "partecipanti" in txt:
            v = first_number(rows)
            if v is not None:
                participants["_total"] = v

    total = participants.pop("_total", None)
    deleghe = participants.get("deleghe") or 0
    rappresentanze = participants.get("rappresentanze") or 0
    if total is not None:
        participants["votanti_normali"] = total - deleghe - rappresentanze

    return build(participants, mode, typology, genre, geography)

def build(participants, mode, typology, genre, geography):
    def fill(d, *keys):
        return {k: d.get(k, None) for k in keys}

    return {
        "participants": fill(participants, "votanti_normali", "rappresentanze", "deleghe"),
        "mode": fill(mode, "a_distanza", "in_presenza"),
        "typology": fill(typology, "persone_fisiche", "persone_giuridiche"),
        "genre": fill(genre, "donne", "uomini"),
        "geography": fill(geography, "italia", "spagna", "estero"),
    }

ZONE_ALIASES = {
    "Monza-Brianza": "Monza e della Brianza",
    "Bolzano": "Bolzano/Bozen",
    "Pesaro-Urbino": "Pesaro e Urbino",
    "Reggio Calabria": "Reggio di Calabria",
    "Reggio Emilia": "Reggio nell'Emilia",
}

def unify_zone(data):
    """Rename totale→votanti so all years share the same field names."""
    if "totale" in data:
        d = dict(data)
        d["votanti"] = d.pop("totale")
        return d
    return data

def normalize_zones(raw_zones):
    italia = {}
    spagna = {}
    for raw_name, data in raw_zones.items():
        name = html.unescape(raw_name)
        name = ZONE_ALIASES.get(name, name)
        entry = unify_zone(data)
        if name == "":
            numeric_fields = ("votanti", "soci", "donne", "uomini", "fisiche", "giuridiche", "presenza", "distanza")
            if any(entry.get(f, 0) for f in numeric_fields):
                print(f"WARNING: zone entry with empty key has non-zero values: {entry}", file=sys.stderr)
            continue
        if name.lower().startswith("fiare"):
            spagna[name] = entry
        else:
            italia[name] = entry
    return {"italia": italia or None, "spagna": spagna or None}

def normalize(path):
    raw = json.loads(path.read_text())
    if "tables" in raw:
        result = from_tables(raw["tables"])
    else:
        result = from_charts(raw)
    raw_zones = raw.get("zones")
    result["zones"] = normalize_zones(raw_zones) if raw_zones else {"italia": None, "spagna": None}
    return result

def main():
    OUT.mkdir(exist_ok=True)
    for path in sorted(DATA.glob("*.json")):
        try:
            result = normalize(path)
            out = OUT / path.name
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"{path.name} -> ok")
        except Exception as e:
            print(f"{path.name} -> ERROR: {e}")

if __name__ == "__main__":
    main()
