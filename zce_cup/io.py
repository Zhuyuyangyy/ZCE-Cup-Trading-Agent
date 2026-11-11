"""Read normalized CSV; vendor-specific data conversion is separate."""
import csv
from .backtest import Bar

def read_bars(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return [Bar(row['timestamp'], float(row['open']), float(row['high']),
                    float(row['low']), float(row['close'])) for row in csv.DictReader(f)]
