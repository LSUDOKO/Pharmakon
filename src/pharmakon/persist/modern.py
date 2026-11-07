"""Stage 7 — modern Greek ethnobotany (published tables only; aggregate species/use level).

* eth_pelion  — Tsioutsiou, Cheilari & Aligiannis 2023, Front. Pharmacol. 14:1225580 (PMC10424924), Table 3. CC BY.
* eth_naegean — Axiotis, Halabalaki & Skaltsounis 2018, Front. Pharmacol. 9:409 (PMC5974156), Suppl. Table 1. CC BY.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd
from lxml import etree

from pharmakon import http
from pharmakon.common import RAW, load_yaml, now_iso
from pharmakon.link.taxonomy import verify_many

STUDIES = {
    "eth_pelion": {"pmcid": "PMC10424924", "year": 2023, "doi": "10.3389/fphar.2023.1225580"},
    "eth_naegean": {"pmcid": "PMC5974156", "year": 2018, "doi": "10.3389/fphar.2018.00409"},
}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def fetch() -> dict:
    out = {}
    for sid, meta in STUDIES.items():
        d = RAW / sid
        d.mkdir(parents=True, exist_ok=True)
        xml = d / f"{meta['pmcid']}.xml"
        if not xml.exists():
            r = http.get(f"{EPMC}/{meta['pmcid']}/fullTextXML")
            r.raise_for_status()
            xml.write_bytes(r.content)
        lic = " ".join(etree.parse(str(xml)).xpath("//license//text()")).strip()
        (d / "LICENSE.txt").write_text(f"{lic}\nDOI: {meta['doi']}\n", encoding="utf-8")
        out[sid] = {"licence": lic[:120]}
    d = RAW / "eth_naegean"
    committed = RAW.parent / "external" / "eth_naegean_Table_1.html"  # LibreOffice conversion, committed (CC BY)
    if not (d / "Table_1.html").exists() and committed.exists():
        (d / "Table_1.html").write_bytes(committed.read_bytes())
    if not (d / "Table_1.html").exists():
        import shutil

        if not shutil.which("soffice"):
            raise SystemExit("North Aegean Suppl. Table 1 is a .doc file: install LibreOffice (soffice) or restore "
                             "data/external/eth_naegean_Table_1.html")
        import io
        import zipfile

        r = http.get(f"{EPMC}/{STUDIES['eth_naegean']['pmcid']}/supplementaryFiles")
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extract("Table_1.doc", d)
        subprocess.run(["soffice", "--headless", "--convert-to", "html", "Table_1.doc", "--outdir", str(d)], cwd=d, check=True, capture_output=True, timeout=180)
        for g in d.glob("*.gif"):
            g.unlink()
    return out


def _use_groups(text: str) -> list[str]:
    kw = load_yaml("use_groups.yaml")["english_keywords"]
    t = " " + re.sub(r"[^a-z ]", " ", str(text).lower()) + " "
    return sorted({g for g, stems in kw.items() for s in stems if re.search(r"\b" + re.escape(s), t)})


def parse_pelion(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW / "eth_pelion" / "PMC10424924.xml"
    t = etree.parse(str(path))
    tw = t.xpath('//table-wrap[@id="T3"]')[0]
    rows, cur = [], None
    for tr in tw.xpath(".//tbody/tr"):
        cells = [" ".join(" ".join(c.itertext()).split()) for c in tr.xpath("./td|./th")]
        if len(cells) < 6:
            continue
        if cells[0]:
            cur = {"botanical": cells[0].split(",")[0].strip(), "family": cells[0].split(",")[-1].strip(), "local_name": cells[1]}
        if cur is None:
            continue
        rows.append({**cur, "plant_part": cells[2], "preparation": cells[3], "application": cells[4], "ailment_text": cells[5]})
    df = pd.DataFrame(rows)
    df["study"] = "eth_pelion"
    # The whole study is about skin ailments: every reported use is dermatological by design.
    df["use_groups"] = df["ailment_text"].map(lambda s: sorted(set(_use_groups(s)) | {"DE"}))
    return df


def parse_naegean(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW / "eth_naegean" / "Table_1.html"
    tables = pd.read_html(path, header=None)
    rows = []
    for tb in tables:
        for r in tb.itertuples(index=False):
            cells = [str(x) if not (isinstance(x, float) and pd.isna(x)) else "" for x in r]
            if len(cells) < 6 or cells[1].lower().startswith("botanical") or not cells[1].strip():
                continue
            bot = re.sub(r"\(.*?\)", "", cells[1]).strip()
            rows.append({"family": cells[0].strip(), "botanical": " ".join(bot.split()), "local_name": " ".join(cells[2].split("(")[0].split()),
                         "plant_part": cells[3], "ailment_text": " ".join(cells[5].split())})
    df = pd.DataFrame(rows)
    df["study"] = "eth_naegean"
    df["use_groups"] = df["ailment_text"].map(_use_groups)
    return df


def build() -> pd.DataFrame:
    fetch()
    df = pd.concat([parse_pelion(), parse_naegean()], ignore_index=True)
    ver = verify_many(df["botanical"].tolist()).set_index("input_name")
    df["taxon_verified"] = df["botanical"].map(ver["verified"]).fillna(False).astype(bool)
    df["taxon_key"] = df["botanical"].map(ver["taxon_key"])
    df["accepted_name"] = df["botanical"].map(ver["accepted_name"])
    df["genus"] = df["botanical"].map(ver["genus"])
    df["study_year"] = df["study"].map({k: v["year"] for k, v in STUDIES.items()})
    df["id_source"] = "field_voucher"  # both studies report herbarium vouchers / botanical identification
    df["p_identity"] = 1.0
    df["source_id"] = df["study"]
    df["retrieved_at"] = now_iso()
    df["method"] = "published_table_parse_v1+gbif_match"
    return df
