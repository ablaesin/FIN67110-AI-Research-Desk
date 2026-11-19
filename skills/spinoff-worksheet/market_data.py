"""Read a user-supplied LSEG close/volume export without copying it into the repository."""
from __future__ import annotations

import csv
import statistics
import zipfile
from datetime import date, datetime, timedelta
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
        sheet_names = [name for name in archive.namelist() if name.startswith("xl/worksheets/") and name.endswith(".xml")]
        if not sheet_names: return []
        root = ET.fromstring(archive.read(sheet_names[0]))
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.text or "" for node in item.findall(".//x:t", NS)) for item in strings.findall("x:si", NS)]
    rows: list[dict[str, str]] = []
    for row in root.findall(".//x:sheetData/x:row", NS):
        record = {}
        for cell in row.findall("x:c", NS):
            column = "".join(letter for letter in cell.attrib["r"] if letter.isalpha())
            item = cell.find("x:v", NS)
            text = item.text if item is not None and item.text else ""
            record[column] = shared[int(text)] if cell.attrib.get("t") == "s" and text else text
        rows.append(record)
    for index, row in enumerate(rows):
        headers = {column: value.strip() for column, value in row.items()}
        normalized = {value.lower() for value in headers.values()}
        if any("date" in value for value in normalized) and "close" in normalized:
            return [{headers[column]: data.get(column, "") for column in headers if headers[column]} for data in rows[index + 1:]]
    if len(rows) < 2: return []
    headers = {column: (rows[0].get(column, "") + " " + rows[1].get(column, "")).strip() for column in rows[0]}
    return [{headers[column]: row.get(column, "") for column in headers if headers[column]} for row in rows[2:]]


def parsed_date(text: str) -> date:
    try: return date.fromisoformat(text.replace("T00:00:00.000Z", ""))
    except ValueError: return (datetime(1899, 12, 30) + timedelta(days=float(text))).date()


def rows(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".xlsx": return xlsx_rows(path)
    with path.open(newline="", encoding="utf-8-sig") as handle: return list(csv.DictReader(handle))


def daily_data(path: Path, ticker: str) -> list[tuple[date, float, float | None]]:
    data = []
    for row in rows(path):
        normalized = {key.strip().lower(): str(item or "").strip() for key, item in row.items()}
        date_text = next((item for key, item in normalized.items() if key in {"date", "exchange date"} or key.endswith(" date")), "")
        close_text = next((item for key, item in normalized.items() if "close" in key), "")
        traded_text = next((item for key, item in normalized.items() if "daily value traded" in key or "turnover" in key), "")
        volume_text = next((item for key, item in normalized.items() if key == "volume" or key.endswith(" volume")), "")
        try:
            close = value(close_text)
            dollars = value(traded_text) if traded_text else close * value(volume_text)
            data.append((parsed_date(date_text), close, dollars))
        except (ValueError, IndexError):
            continue
    return sorted(data)


def first_close_after(path: Path, ticker: str, after: date) -> tuple[date, float] | None:
    return next(((day, close) for day, close, _ in daily_data(path, ticker) if day > after), None)


def median_dollar_volume(path: Path, ticker: str) -> float | None:
    values = [dollars for _, _, dollars in daily_data(path, ticker) if dollars is not None]
    return statistics.median(values) if values else None
