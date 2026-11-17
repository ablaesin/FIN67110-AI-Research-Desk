"""Read a user-supplied LSEG close/volume export without copying it into the repository."""
from __future__ import annotations

import csv
import statistics
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def value(text: str) -> float:
    clean = text.replace("\u202f", "").replace(",", "").strip()
    multiplier = 1
    if clean[-1:].upper() == "K": clean, multiplier = clean[:-1], 1_000
    if clean[-1:].upper() == "M": clean, multiplier = clean[:-1], 1_000_000
    if clean[-1:].upper() == "B": clean, multiplier = clean[:-1], 1_000_000_000
    return float(clean.strip()) * multiplier


def xlsx_rows(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in root.findall(".//x:sheetData/x:row", NS):
        record = {}
        for cell in row.findall("x:c", NS):
            column = "".join(letter for letter in cell.attrib["r"] if letter.isalpha())
            item = cell.find("x:v", NS)
            record[column] = item.text if item is not None and item.text else ""
        rows.append(record)
    headers = {column: rows[0].get(column, "") + " " + rows[1].get(column, "") for column in rows[0]}
    return [{headers[column].strip(): row.get(column, "") for column in headers} for row in rows[2:]]


def rows(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".xlsx": return xlsx_rows(path)
    with path.open(newline="", encoding="utf-8-sig") as handle: return list(csv.DictReader(handle))


def daily_data(path: Path, ticker: str) -> list[tuple[date, float, float | None]]:
    data = []
    for row in rows(path):
        normalized = {key.strip().lower(): str(item or "").strip() for key, item in row.items()}
        date_text = next((item for key, item in normalized.items() if key == "date"), "").replace("T00:00:00.000Z", "")
        close_text = next((item for key, item in normalized.items() if "close" in key), "")
        traded_text = next((item for key, item in normalized.items() if "daily value traded" in key), "")
        volume_text = next((item for key, item in normalized.items() if key == "volume" or key.endswith(" volume")), "")
        try:
            close = value(close_text)
            dollars = value(traded_text) if traded_text else close * value(volume_text)
            data.append((date.fromisoformat(date_text), close, dollars))
        except (ValueError, IndexError):
            continue
    return sorted(data)


def first_close_after(path: Path, ticker: str, after: date) -> tuple[date, float] | None:
    return next(((day, close) for day, close, _ in daily_data(path, ticker) if day > after), None)


def median_dollar_volume(path: Path, ticker: str) -> float | None:
    values = [dollars for _, _, dollars in daily_data(path, ticker) if dollars is not None]
    return statistics.median(values) if values else None
