#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Export zone data to CSV at four aggregation levels (long format: one row per year × zone).

Outputs:
  csv/zones_total.csv       — one row per year (grand total, all zones summed)
  csv/zones_by_country.csv  — one row per (year, paese)
  csv/zones_by_area.csv     — one row per (year, area)
  csv/zones_by_province.csv — one row per (year, provincia) with area column
"""
import csv
import json
from collections import Counter
from pathlib import Path

NORMALIZED = Path("normalized")
OUT = Path("csv")

MONTH_IT = {
    "01": "Gen", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "Mag", "06": "Giu", "07": "Lug", "08": "Ago",
    "09": "Set", "10": "Ott", "11": "Nov", "12": "Dic",
}

PROVINCE_AREA = {
    "Agrigento": "Isole", "Alessandria": "Nord-Ovest", "Ancona": "Centro",
    "Aosta": "Nord-Ovest", "Arezzo": "Centro", "Ascoli Piceno": "Centro",
    "Asti": "Nord-Ovest", "Avellino": "Sud", "Bari": "Sud",
    "Barletta-Andria-Trani": "Sud", "Belluno": "Nord-Est", "Benevento": "Sud",
    "Bergamo": "Nord-Ovest", "Biella": "Nord-Ovest", "Bologna": "Nord-Est",
    "Bolzano/Bozen": "Nord-Est", "Brescia": "Nord-Ovest", "Brindisi": "Sud",
    "Cagliari": "Isole", "Caltanissetta": "Isole", "Campobasso": "Sud",
    "Caserta": "Sud", "Catania": "Isole", "Catanzaro": "Sud",
    "Chieti": "Sud", "Como": "Nord-Ovest", "Cosenza": "Sud",
    "Cremona": "Nord-Ovest", "Crotone": "Sud", "Cuneo": "Nord-Ovest",
    "Enna": "Isole", "Fermo": "Centro", "Ferrara": "Nord-Est",
    "Firenze": "Centro", "Foggia": "Sud", "Forlì-Cesena": "Nord-Est",
    "Frosinone": "Centro", "Genova": "Nord-Ovest", "Gorizia": "Nord-Est",
    "Grosseto": "Centro", "Imperia": "Nord-Ovest", "Isernia": "Sud",
    "La Spezia": "Nord-Ovest", "L'Aquila": "Sud", "Latina": "Centro",
    "Lecce": "Sud", "Lecco": "Nord-Ovest", "Livorno": "Centro",
    "Lodi": "Nord-Ovest", "Lucca": "Centro", "Macerata": "Centro",
    "Mantova": "Nord-Ovest", "Massa-Carrara": "Centro", "Matera": "Sud",
    "Messina": "Isole", "Milano": "Nord-Ovest", "Modena": "Nord-Est",
    "Monza e della Brianza": "Nord-Ovest", "Napoli": "Sud", "Novara": "Nord-Ovest",
    "Nuoro": "Isole", "Oristano": "Isole", "Padova": "Nord-Est",
    "Palermo": "Isole", "Parma": "Nord-Est", "Pavia": "Nord-Ovest",
    "Perugia": "Centro", "Pesaro e Urbino": "Centro", "Pescara": "Sud",
    "Piacenza": "Nord-Est", "Pisa": "Centro", "Pistoia": "Centro",
    "Pordenone": "Nord-Est", "Potenza": "Sud", "Prato": "Centro",
    "Ragusa": "Isole", "Ravenna": "Nord-Est", "Reggio di Calabria": "Sud",
    "Reggio nell'Emilia": "Nord-Est", "Rieti": "Centro", "Rimini": "Nord-Est",
    "Roma": "Centro", "Rovigo": "Nord-Est", "Salerno": "Sud",
    "Sassari": "Isole", "Savona": "Nord-Ovest", "Siena": "Centro",
    "Siracusa": "Isole", "Sondrio": "Nord-Ovest", "Sud Sardegna": "Isole",
    "Taranto": "Sud", "Teramo": "Sud", "Terni": "Centro",
    "Torino": "Nord-Ovest", "Trapani": "Isole", "Trento": "Nord-Est",
    "Treviso": "Nord-Est", "Trieste": "Nord-Est", "Udine": "Nord-Est",
    "Varese": "Nord-Ovest", "Venezia": "Nord-Est", "Verbano-Cusio-Ossola": "Nord-Ovest",
    "Vercelli": "Nord-Ovest", "Verona": "Nord-Est", "Vibo Valentia": "Sud",
    "Vicenza": "Nord-Est", "Viterbo": "Centro",
}

AREA_ORDER = ["Nord-Ovest", "Nord-Est", "Centro", "Sud", "Isole"]
FIELDS = ["votanti", "donne", "in_presenza", "a_distanza"]


def label_for(stem, multi_month_years):
    year, month = stem.split(".")
    return f"{year} {MONTH_IT[month]}" if year in multi_month_years else year


def load_data():
    return {p.stem: json.loads(p.read_text()) for p in sorted(NORMALIZED.glob("*.json"))}


def sum_zones(zone_dict, names):
    result = {}
    for n in names:
        z = (zone_dict or {}).get(n)
        if not z:
            continue
        for k, v in z.items():
            if v is not None:
                result[k] = result.get(k, 0) + v
    return result or None


def fmt(v):
    return "" if v is None else str(v)


def write_csv(path, header, rows):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"Written {path} ({len(rows)} rows)")


def zone_row(z, anno, extra_cols):
    z = z or {}
    return [anno] + extra_cols + [fmt(z.get(f)) for f in FIELDS]


def build():
    data = load_data()
    stems = sorted(data.keys())
    year_counts = Counter(k.split(".")[0] for k in stems)
    multi_month_years = {y for y, c in year_counts.items() if c > 1}
    labels = {s: label_for(s, multi_month_years) for s in stems}

    # --- zones_total.csv: one row per year, grand sum of all Italian + Spanish zones ---
    header = ["anno"] + FIELDS
    rows = []
    for s in stems:
        z = data[s].get("zones", {})
        it = z.get("italia") or {}
        es = z.get("spagna") or {}
        total = sum_zones({**it, **es}, list(it) + list(es))
        rows.append(zone_row(total, labels[s], []))
    write_csv(OUT / "zones_total.csv", header, rows)

    # --- zones_by_country.csv: one row per (year, paese) ---
    header = ["anno", "paese"] + FIELDS
    rows = []
    for s in stems:
        z = data[s].get("zones", {})
        it = z.get("italia") or {}
        es = z.get("spagna") or {}
        for paese, zones in [("Italia", it), ("Spagna", es)]:
            if zones:
                rows.append(zone_row(sum_zones(zones, list(zones)), labels[s], [paese]))
    write_csv(OUT / "zones_by_country.csv", header, rows)

    # --- zones_by_area.csv: one row per (year, paese, area) ---
    header = ["anno", "paese", "area"] + FIELDS
    rows = []
    for s in stems:
        z = data[s].get("zones", {})
        it = z.get("italia") or {}
        es = z.get("spagna") or {}
        for area in AREA_ORDER:
            names = [n for n in it if PROVINCE_AREA.get(n) == area]
            if names:
                rows.append(zone_row(sum_zones(it, names), labels[s], ["Italia", area]))
        if es:
            rows.append(zone_row(sum_zones(es, list(es)), labels[s], ["Spagna", "Fiare"]))
    write_csv(OUT / "zones_by_area.csv", header, rows)

    # --- zones_by_province.csv: one row per (year, paese, area, province) ---
    header = ["anno", "paese", "area", "provincia"] + FIELDS
    rows = []
    for s in stems:
        z = data[s].get("zones", {})
        it = z.get("italia") or {}
        es = z.get("spagna") or {}
        for area in AREA_ORDER:
            for prov in sorted(n for n in it if PROVINCE_AREA.get(n) == area):
                rows.append(zone_row(it[prov], labels[s], ["Italia", area, prov]))
        for fiare in sorted(es):
            rows.append(zone_row(es[fiare], labels[s], ["Spagna", "Fiare", fiare]))
    write_csv(OUT / "zones_by_province.csv", header, rows)


if __name__ == "__main__":
    build()
