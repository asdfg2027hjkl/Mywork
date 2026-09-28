# China Merchants Bank (CMB) Exchange Rate Spider

## Project Overview
A Python-based web scraping project designed to fetch real-time foreign exchange rates from China Merchants Bank (CMB) and persist the data into an SQLite database.

## Features
- Uses the `requests` library with spoofed headers to bypass basic anti-scraping mechanisms.
- Fetches and parses JSON data from real-time exchange rate APIs.
- Encapsulates spider logic using Object-Oriented Programming (the `MySpider` class).
- Utilizes `sqlite3` to save data into a local `rates.db` database.

## Prerequisites
- Python 3.x
- `requests` library

## Usage
1. Clone or download this repository.
2. Install the required dependency:
   ```bash
   pip install requests