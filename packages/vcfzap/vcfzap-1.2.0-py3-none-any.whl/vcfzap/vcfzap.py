#!/usr/bin/env python3
"""
vcfzap - Extract contacts from VCF files to CSV, TXT, JSON, HTML, SQLite, or terminal preview.

Extracts contact information (name, phone numbers, email, address, organization) from VCF files
and outputs to CSV, TXT, JSON, HTML, SQLite, or terminal preview. Supports limiting contacts,
timestamped filenames, color/no-color output, encoding detection, quiet mode, no-logs,
non-interactive execution, pretty-printed JSON, name-based filtering with --search-name (supports multiple names),
and phone number filtering with --search-number (supports multiple patterns).
"""

import argparse
import csv
import datetime
import json
import logging
import sys
import os
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from itertools import islice
from html import escape
import shutil  # For terminal width detection
import textwrap  # For wrapping long text

try:
    import vobject
except ImportError:
    print("Error: Missing 'vobject' module. Install it using: pip install vobject", file=sys.stderr)
    sys.exit(1)

try:
    import chardet
except ImportError:
    print("Error: Missing 'chardet' module. Install it using: pip install chardet", file=sys.stderr)
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Error: Missing 'tqdm' module. Install it using: pip install tqdm", file=sys.stderr)
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("Error: Missing 'colorama' module. Install it using: pip install colorama", file=sys.stderr)
    sys.exit(1)

__version__ = "1.2.0"
DEFAULT_ENCODING = "utf-8"
VALID_FIELDS = {"name", "phone", "email", "address", "organization"}
VALID_CSV_DELIMITERS = ",;:|^"
MB = 1024 * 1024  # 1MB in bytes
CHUNK_SIZE = 512 * MB  # 512KB for encoding detection

def setup_logging(log_file: Optional[str] = None, no_logs: bool = False, verbose: bool = False) -> None:
    """Configure logging with a clean, professional format."""
    logger = logging.getLogger('vcfzap')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers = []

    if no_logs:
        logger.handlers = [logging.NullHandler()]
        return

    # Clean log format without timestamp for clarity
    log_format = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_file = f"{log_file}.txt" if not log_file.endswith(".txt") else log_file
        log_file_path = Path(log_file).resolve()
        log_dir = log_file_path.parent
        if not log_dir.is_dir():
            cprint(f"Error: Log file directory '{log_dir}' does not exist", "red", False, False)
            sys.exit(1)
        if not os.access(log_dir, os.W_OK):
            cprint(f"Error: No write permission for log file directory '{log_dir}'", "red", False, False)
            sys.exit(1)
        try:
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging initialized to file: {log_file_path}")
        except IOError as e:
            cprint(f"Error: Failed to initialize log file '{log_file_path}': {e}", "red", False, False)
            sys.exit(1)

def cprint(text: str, color: str = "red", no_color: bool = False, quiet: bool = False) -> None:
    """Print colored text to console without logging, respecting quiet mode."""
    if quiet and color != "red":
        return
    colors = {"red": Fore.RED, "green": Fore.GREEN, "blue": Fore.BLUE, "yellow": Fore.YELLOW, "cyan": Fore.CYAN}
    print(
        text if no_color or color not in colors else f"{colors[color]}{text}{Style.RESET_ALL}",
        file=sys.stderr if color == "red" else sys.stdout
    )

def validate_file(
    path: str, ext: str, is_input: bool, max_size_mb: int, no_color: bool, quiet: bool, no_prompt: bool = False
) -> Path:
    """Validate input or output file path and return Path object."""
    logger = logging.getLogger('vcfzap')
    if not path:
        cprint(f"Error: {'Input' if is_input else f'--{ext}'} requires a valid file path", "red", no_color, quiet)
        logger.error(f"No {'input' if is_input else f'--{ext}'} file path provided")
        sys.exit(1)
    path = Path(path).resolve()
    logger.debug(f"Validating {'input' if is_input else 'output'} file: {path}")

    if is_input:
        if path.suffix.lower() != ".vcf":
            cprint("Error: Input file must have a .vcf extension", "red", no_color, quiet)
            logger.error(f"Invalid file extension for '{path}': must be .vcf")
            sys.exit(1)
        if not path.is_file():
            cprint(f"Error: File '{path}' does not exist", "red", no_color, quiet)
            logger.error(f"Input file does not exist: {path}")
            sys.exit(1)
        if not os.access(path, os.R_OK):
            cprint(f"Error: File '{path}' is not readable. Check permissions", "red", no_color, quiet)
            logger.error(f"Input file not readable: {path}")
            sys.exit(1)
        if path.stat().st_size > max_size_mb * MB:
            if no_prompt:
                cprint(f"Large file detected, proceeding due to --no-prompt: {path} ({path.stat().st_size / MB:.2f}MB)", "yellow", no_color, quiet)
                logger.info(f"Large input file detected, proceeding: {path} ({path.stat().st_size / MB:.2f}MB)")
            else:
                cprint(f"Warning: File '{path}' is large ({path.stat().st_size / MB:.2f}MB). Continue? (y/n): ", "yellow", no_color, quiet)
                logger.warning(f"Large input file: {path} ({path.stat().st_size / MB:.2f}MB)")
                try:
                    if input().strip().lower() != 'y':
                        cprint("Operation cancelled", "red", no_color, quiet)
                        logger.info("Operation cancelled due to large input file")
                        sys.exit(0)
                except KeyboardInterrupt:
                    cprint("Operation cancelled by user", "red", no_color, quiet)
                    logger.info("Operation cancelled by user")
                    sys.exit(0)
    else:
        if path.suffix.lower() != f".{ext}":
            cprint(f"Error: Output filename must end with .{ext}", "red", no_color, quiet)
            logger.error(f"Invalid output file extension for '{path}': must be .{ext}")
            sys.exit(1)
        directory = path.parent
        if not directory.is_dir():
            cprint(f"Error: Output directory '{directory}' does not exist", "red", no_color, quiet)
            logger.error(f"Output directory does not exist: {directory}")
            sys.exit(1)
        if not os.access(directory, os.W_OK):
            cprint(f"Error: No write permission for directory '{directory}'", "red", no_color, quiet)
            logger.error(f"No write permission for output directory: {directory}")
            sys.exit(1)
        if path.exists() and not path.is_dir():
            if not os.access(path, os.W_OK):
                cprint(f"Error: File '{path}' exists but is not writable. Check permissions", "red", no_color, quiet)
                logger.error(f"Output file not writable: {path}")
                sys.exit(1)
            if no_prompt:
                cprint(f"File '{path}' exists, overwriting due to --no-prompt", "yellow", no_color, quiet)
                logger.info(f"Overwriting existing output file: {path}")
            else:
                cprint(f"Warning: File '{path}' already exists", "yellow", no_color, quiet)
                logger.warning(f"Output file already exists: {path}")
                try:
                    if input("Overwrite? (y/n): ").strip().lower() != 'y':
                        cprint("Operation cancelled", "red", no_color, quiet)
                        logger.info("Operation cancelled due to existing output file")
                        sys.exit(0)
                except KeyboardInterrupt:
                    cprint("Operation cancelled by user", "red", no_color, quiet)
                    logger.info("Operation cancelled by user")
                    sys.exit(0)
    logger.debug(f"Validated {'input' if is_input else 'output'} file: {path}")
    return path

def detect_file_encoding(file_path: Path, no_color: bool, quiet: bool) -> str:
    """Detect file encoding using chardet with chunked reading and fallback to UTF-8."""
    logger = logging.getLogger('vcfzap')
    try:
        with file_path.open("rb") as f:
            raw_data = f.read(CHUNK_SIZE)
            result = chardet.detect(raw_data)
            encoding = result["encoding"] or DEFAULT_ENCODING
            confidence = result.get('confidence', 0.0)
            if confidence < 0.5:
                logger.warning(f"Low confidence ({confidence:.2f}) in detected encoding: {encoding}, using {DEFAULT_ENCODING}")
                encoding = DEFAULT_ENCODING
            cprint(f"Detected encoding: {encoding} (confidence: {confidence:.2f})", "blue", no_color, quiet)
            logger.debug(f"Detected encoding for '{file_path}': {encoding} (confidence: {confidence:.2f})")
            return encoding
    except IOError as e:
        cprint(f"Error detecting encoding: {e}", "red", no_color, quiet)
        logger.error(f"Failed to detect encoding for '{file_path}': {e}")
        return DEFAULT_ENCODING

def clean_phone_number(phone: str) -> str:
    """Clean phone number, preserving '+' and extensions."""
    if not phone:
        return ""
    cleaned = ''.join(char for char in phone if char.isdigit() or char in '+;ext=')
    return cleaned if cleaned.startswith('+') else cleaned.lstrip('+')

def format_address(adr: Any) -> str:
    """Format VCF address into a readable string."""
    if not adr or not hasattr(adr, 'value'):
        return ""
    parts = [part.strip() for part in (
        getattr(adr.value, attr, "") for attr in ['street', 'city', 'region', 'code', 'country']
    ) if part.strip()]
    return ", ".join(parts) or ""

def normalize_value(val: Any) -> str:
    """Normalize any value to a string, handling lists, None, and complex objects."""
    if val is None:
        return ""
    if isinstance(val, list):
        return ", ".join(normalize_value(item) for item in val if item)
    if isinstance(val, vobject.vcard.Name):
        return str(val).strip() or ""
    return str(val).strip()

def wrap_text(text: str, width: int) -> List[str]:
    """Wrap text to fit within the specified width."""
    if not text:
        return [""]
    return textwrap.wrap(text, width=width, replace_whitespace=False, drop_whitespace=True)

def write_csv(filepath: Path, contacts: List[Dict[str, Any]], delimiter: str, no_color: bool, quiet: bool) -> None:
    """Write contacts to CSV file with customizable delimiter."""
    logger = logging.getLogger('vcfzap')
    if not contacts:
        cprint(f"No contacts to write to CSV file: {filepath}", "yellow", no_color, quiet)
        logger.info(f"No contacts to write to CSV: {filepath}")
        return
    try:
        with filepath.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter, lineterminator='\n')
            headers = ["S.No"] + [key.capitalize() for key in contacts[0].keys()]
            writer.writerow(headers)
            for i, contact in enumerate(contacts, 1):
                writer.writerow([i] + [normalize_value(val) for val in contact.values()])
        logger.info(f"Wrote {len(contacts)} contacts to CSV: {filepath}")
    except IOError as e:
        cprint(f"Error writing CSV file: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write CSV to '{filepath}': {e}")
        sys.exit(1)

def write_txt(filepath: Path, contacts: List[Dict[str, Any]], no_color: bool, quiet: bool) -> None:
    """Write contacts to TXT file in a readable format."""
    logger = logging.getLogger('vcfzap')
    if not contacts:
        cprint(f"No contacts to write to TXT file: {filepath}", "yellow", no_color, quiet)
        logger.info(f"No contacts to write to TXT: {filepath}")
        return
    try:
        with filepath.open("w", encoding="utf-8") as f:
            for i, contact in enumerate(contacts, 1):
                fields = [f"{key.capitalize()}: {normalize_value(val)}" for key, val in contact.items()]
                f.write(f"{i:02d}. {' | '.join(fields)}\n")
        logger.info(f"Wrote {len(contacts)} contacts to TXT: {filepath}")
    except IOError as e:
        cprint(f"Error writing TXT file: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write TXT to '{filepath}': {e}")
        sys.exit(1)

def write_json(filepath: Path, contacts: List[Dict[str, Any]], pretty: bool, no_color: bool, quiet: bool) -> None:
    """Write contacts to JSON file, with optional pretty-printing."""
    logger = logging.getLogger('vcfzap')
    if not contacts:
        try:
            with filepath.open("w", encoding="utf-8") as f:
                f.write("[]")
            logger.info(f"Wrote empty JSON to: {filepath}")
        except PermissionError as e:
            cprint(f"Error: No write permission for '{filepath}': {e}", "red", no_color, quiet)
            logger.error(f"Failed to write empty JSON to '{filepath}': {e}")
            sys.exit(1)
        except IOError as e:
            cprint(f"Error writing JSON file: {e}", "red", no_color, quiet)
            logger.error(f"Failed to write empty JSON to '{filepath}': {e}")
            sys.exit(1)
        return

    data = [{"id": i, **{k: normalize_value(v) for k, v in contact.items()}} for i, contact in enumerate(contacts, 1)]
    temp_filepath = filepath.with_suffix(".tmp")
    try:
        with temp_filepath.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2 if pretty else None)
        # Atomically replace the original file
        shutil.move(temp_filepath, filepath)
        logger.info(f"Wrote {len(contacts)} contacts to JSON: {filepath}")
    except PermissionError as e:
        cprint(f"Error: No write permission for '{filepath}': {e}", "red", no_color, quiet)
        logger.error(f"Failed to write JSON to '{filepath}': {e}")
        if temp_filepath.exists():
            temp_filepath.unlink()
        sys.exit(1)
    except IOError as e:
        cprint(f"Error writing JSON file: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write JSON to '{filepath}': {e}")
        if temp_filepath.exists():
            temp_filepath.unlink()
        sys.exit(1)
    except json.JSONEncodeError as e:
        cprint(f"Error: Invalid JSON data: {e}", "red", no_color, quiet)
        logger.error(f"Failed to encode JSON for '{filepath}': {e}")
        if temp_filepath.exists():
            temp_filepath.unlink()
        sys.exit(1)
    finally:
        if temp_filepath.exists():
            temp_filepath.unlink()

def write_html_file(filepath: Path, contacts: List[Dict[str, Any]], no_color: bool, quiet: bool) -> None:
    """Write contacts to HTML file with a search bar and professional dark/light theme support."""
    logger = logging.getLogger('vcfzap')
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VCF Contacts</title>
    <style>
        :root {
            /* Default light theme */
            --bg-color: #ffffff;
            --card-bg: #f9f9f9;
            --text-color: #333333;
            --accent-color: #2e7d32;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            --field-text: #555555;
            --field-label: #1b5e20;
            --separator: rgba(46, 125, 50, 0.3);

            /* Dark theme overrides */
            [data-theme="dark"] {
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --text-color: #e0e0e0;
                --accent-color: #66bb6a;
                --shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                --field-text: #bbbbbb;
                --field-label: #a5d6a7;
                --separator: rgba(102, 187, 106, 0.3);
            }
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Roboto', 'Helvetica', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            transition: all 0.3s ease;
        }

        .container {
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
        }

        .search-bar {
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 20px;
            border: 2px solid var(--accent-color);
            border-radius: 8px;
            font-size: 1.1em;
            color: var(--text-color);
            background: var(--card-bg);
            box-shadow: var(--shadow);
            transition: box-shadow 0.3s ease;
        }

        .search-bar:focus {
            outline: none;
            box-shadow: 0 0 8px var(--accent-color);
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            border: 2px solid var(--accent-color);
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            color: var(--text-color);
            font-weight: 500;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }

        .theme-toggle:hover {
            transform: scale(1.05);
            background: color-mix(in srgb, var(--card-bg), var(--accent-color) 10%);
        }

        h1 {
            text-align: center;
            color: var(--text-color);
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            border-bottom: 3px solid var(--accent-color);
            padding-bottom: 10px;
        }

        .contact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            padding: 20px 0;
        }

        .contact-card {
            background: var(--card-bg);
            border-radius: 10px;
            box-shadow: var(--shadow);
            padding: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .contact-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }

        .contact-card h2 {
            font-size: 1.5em;
            color: var(--text-color);
            margin: 0 0 15px 0;
            font-weight: 600;
            text-transform: uppercase;
        }

        .contact-field {
            margin-bottom: 15px;
            color: var(--field-text);
            font-size: 1em;
            line-height: 1.6;
        }

        .contact-field span {
            font-weight: 600;
            color: var(--field-label);
        }

        .contact-field hr {
            border: 0;
            height: 1px;
            background: var(--separator);
            margin: 8px 0 12px 0;
        }

        .no-contacts {
            text-align: center;
            color: var(--field-text);
            font-size: 1.2em;
            padding: 20px;
            background: var(--card-bg);
            border-radius: 10px;
            box-shadow: var(--shadow);
            font-weight: 500;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2em;
            }
            .contact-grid {
                grid-template-columns: 1fr;
            }
            .contact-card {
                padding: 15px;
            }
            .theme-toggle {
                top: 15px;
                right: 15px;
                padding: 8px 16px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <input type="text" class="search-bar" placeholder="Search by Name, Phone, Organization, Address, Email, S.No, or Contact #..." onkeyup="filterContacts()">
        <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
        <h1>VCF Contacts</h1>
        <div class="contact-grid" id="contactGrid">
"""
    if contacts:
        for i, contact in enumerate(contacts, 1):
            html_content += f"            <div class=\"contact-card\" data-sno=\"{i}\" data-name=\"{escape(normalize_value(contact.get('name', '')))}\" data-phone=\"{escape(normalize_value(contact.get('phone', '')))}\" data-org=\"{escape(normalize_value(contact.get('organization', '')))}\" data-addr=\"{escape(normalize_value(contact.get('address', '')))}\" data-email=\"{escape(normalize_value(contact.get('email', '')))}\">\n"
            html_content += f"                <h2>Contact #{i}</h2>\n"
            for key, val in contact.items():
                value = normalize_value(val)
                if value:
                    html_content += f"                <div class=\"contact-field\"><span>{key.capitalize()}:</span> {escape(value)}<hr></div>\n"
            html_content += "            </div>\n"
    else:
        html_content += "            <div class=\"no-contacts\">No contacts found</div>\n"
    html_content += """
        </div>
    </div>
    <script>
        // Load system or saved theme
        function applyTheme() {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark' || (!savedTheme && prefersDark.matches)) {
                document.body.setAttribute('data-theme', 'dark');
            } else {
                document.body.removeAttribute('data-theme');
            }
        }

        function toggleTheme() {
            const body = document.body;
            const isDark = body.getAttribute('data-theme') === 'dark';
            body.setAttribute('data-theme', isDark ? 'light' : 'dark');
            localStorage.setItem('theme', isDark ? 'light' : 'dark');
        }

        // Filter contacts
        function filterContacts() {
            const searchTerm = document.querySelector('.search-bar').value.toLowerCase();
            const cards = document.querySelectorAll('.contact-card');
            cards.forEach(card => {
                const sno = card.getAttribute('data-sno').toLowerCase();
                const name = card.getAttribute('data-name').toLowerCase();
                const phone = card.getAttribute('data-phone').toLowerCase();
                const org = card.getAttribute('data-org').toLowerCase();
                const addr = card.getAttribute('data-addr').toLowerCase();
                const email = card.getAttribute('data-email').toLowerCase();
                const match = sno.includes(searchTerm) || name.includes(searchTerm) || phone.includes(searchTerm) ||
                              org.includes(searchTerm) || addr.includes(searchTerm) || email.includes(searchTerm);
                card.style.display = match ? 'block' : 'none';
            });
            // Show no-contacts message if no matches
            const noContacts = document.querySelector('.no-contacts');
            if (noContacts) {
                noContacts.style.display = [...cards].every(card => card.style.display === 'none') ? 'block' : 'none';
            }
        }

        // Initial load
        window.onload = function() {
            applyTheme();
            filterContacts(); // Initial filter in case of pre-filled search
            const searchBar = document.querySelector('.search-bar');
            searchBar.addEventListener('input', filterContacts);
            // Add Google Fonts
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap';
            document.head.appendChild(link);
        };

        // Update theme on system preference change
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
    </script>
</body>
</html>
"""
    try:
        with filepath.open("w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Wrote {len(contacts)} contacts to HTML: {filepath}")
    except IOError as e:
        cprint(f"Error writing HTML file: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write HTML to '{filepath}': {e}")
        sys.exit(1)

def write_sqlite(filepath: Path, contacts: List[Dict[str, Any]], fields: List[str], no_color: bool, quiet: bool) -> None:
    """Write contacts to SQLite database, clearing existing data if overwriting."""
    logger = logging.getLogger('vcfzap')
    if not contacts:
        cprint(f"No contacts to write to SQLite database: {filepath}", "yellow", no_color, quiet)
        logger.info(f"No contacts to write to SQLite: {filepath}")
        return

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()

        # Create table creation query dynamically based on fields
        columns = ["id INTEGER PRIMARY KEY"] + [f"{field} TEXT" for field in fields]
        create_table_query = f"CREATE TABLE IF NOT EXISTS contacts ({', '.join(columns)})"
        cursor.execute(create_table_query)

        # Clear existing data in the contacts table to avoid UNIQUE constraint violations
        cursor.execute("DELETE FROM contacts")

        # Prepare insert query
        placeholders = ", ".join(["?"] * (len(fields) + 1))  # +1 for id
        insert_query = f"INSERT INTO contacts (id, {', '.join(fields)}) VALUES ({placeholders})"

        # Insert contacts
        for i, contact in enumerate(contacts, 1):
            values = [i] + [normalize_value(contact.get(field, "")) for field in fields]
            cursor.execute(insert_query, values)

        # Commit changes and close connection
        conn.commit()
        logger.info(f"Wrote {len(contacts)} contacts to SQLite: {filepath}")
    except sqlite3.Error as e:
        cprint(f"Error writing SQLite database: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write SQLite to '{filepath}': {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

def preview_contacts(contacts: List[Dict[str, Any]], no_color: bool, quiet: bool, max_column_width: int) -> None:
    """Display contacts in a formatted, expandable table in the terminal."""
    logger = logging.getLogger('vcfzap')
    if quiet:
        logger.debug("Skipping preview due to quiet mode")
        return

    if not contacts:
        cprint("No contacts found", "yellow", no_color, quiet)
        logger.info("No contacts found for preview")
        return

    logger.info(f"Previewing {len(contacts)} contacts in terminal")
    console_width = shutil.get_terminal_size((80, 20)).columns
    keys = contacts[0].keys()
    headers = ["No"] + [key.capitalize() for key in keys]
    min_width = 5  # Minimum width for "No" column

    max_lengths = {"No": max(len(str(len(contacts))), 2)}
    for key in keys:
        max_lengths[key] = max(len(key.capitalize()), 
                               max(len(line) for contact in contacts 
                                   for line in wrap_text(normalize_value(contact.get(key, "")), max_column_width)))

    total_columns = len(headers)
    padding_per_column = 2
    border_overhead = 2
    available_width = console_width - (total_columns * padding_per_column + border_overhead)

    total_content_width = sum(max_lengths.values())
    col_widths = {}
    if total_content_width > available_width:
        scale_factor = available_width / total_content_width
        for key in max_lengths:
            col_widths[key] = max(min_width if key == "No" else 10, 
                                 min(int(max_lengths[key] * scale_factor), max_column_width))
    else:
        for key in max_lengths:
            col_widths[key] = min(max_lengths[key], max_column_width)

    while sum(col_widths.values()) + (total_columns * padding_per_column + border_overhead) > console_width:
        excess = sum(col_widths.values()) + (total_columns * padding_per_column + border_overhead) - console_width
        reduction_per_column = excess // total_columns
        for key in col_widths:
            col_widths[key] = max(min_width if key == "No" else 10, col_widths[key] - reduction_per_column)
        if reduction_per_column == 0:
            break

    table_data = []
    max_lines_per_row = 0
    for i, contact in enumerate(contacts, 1):
        row = []
        no_lines = wrap_text(str(i), col_widths["No"])
        row.append(no_lines)
        max_lines = len(no_lines)
        for key in keys:
            value = normalize_value(contact.get(key, ""))
            wrapped = wrap_text(value, col_widths[key])
            row.append(wrapped)
            max_lines = max(max_lines, len(wrapped))
        table_data.append(row)
        max_lines_per_row = max(max_lines_per_row, max_lines)

    try:
        header_lines = []
        for header, key in zip(headers, ["No"] + list(keys)):
            wrapped = wrap_text(header, col_widths[key])
            header_lines.append(wrapped + [""] * (max_lines_per_row - len(wrapped)))

        top_border = "┌" + "┬".join("─" * (col_widths[key] + padding_per_column) for key in ["No"] + list(keys)) + "┐"
        print(top_border if no_color else f"{Fore.CYAN}{top_border}{Style.RESET_ALL}")

        for i in range(max_lines_per_row):
            row_parts = []
            for j, key in enumerate(["No"] + list(keys)):
                cell = header_lines[j][i] if i < len(header_lines[j]) else ""
                row_parts.append(f"│ {cell.ljust(col_widths[key])} ")
            row = "".join(row_parts) + "│"
            print(row if no_color else f"{Fore.CYAN}{row}{Style.RESET_ALL}")

        sep = "├" + "┼".join("─" * (col_widths[key] + padding_per_column) for key in ["No"] + list(keys)) + "┤"
        print(sep if no_color else f"{Fore.CYAN}{sep}{Style.RESET_ALL}")

        for row_idx, row in enumerate(table_data):
            for i in range(max_lines_per_row):
                row_parts = []
                for j, (cell, key) in enumerate(zip(row, ["No"] + list(keys))):
                    cell_content = cell[i] if i < len(cell) else ""
                    row_parts.append(f"│ {cell_content.ljust(col_widths[key])} ")
                print("".join(row_parts) + "│")
            if row_idx < len(table_data) - 1:
                row_sep = "├" + "┼".join("─" * (col_widths[key] + padding_per_column) for key in ["No"] + list(keys)) + "┤"
                print(row_sep)

        bottom_border = "└" + "┴".join("─" * (col_widths[key] + padding_per_column) for key in ["No"] + list(keys)) + "┘"
        print(bottom_border if no_color else f"{Fore.CYAN}{bottom_border}{Style.RESET_ALL}")
    except Exception as e:
        cprint(f"Error rendering table: {e}. Falling back to simple output", "yellow", no_color, quiet)
        logger.warning(f"Failed to render table, using simple output: {e}")
        print("No  " + "  ".join(key.capitalize() for key in keys))
        print("-" * console_width)
        for i, contact in enumerate(contacts, 1):
            values = [normalize_value(contact.get(key, "")).ljust(col_widths[key]) for key in keys]
            print(f"{str(i):<3} " + "  ".join(values))

def truncate_text(text: str, width: int) -> str:
    """Truncate text to fit within the specified width, adding ellipsis if needed."""
    if len(text) <= width:
        return text
    return text[:width - 3] + "..."

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments with mutually exclusive output options."""
    parser = argparse.ArgumentParser(
        description="vcfzap - Extract contacts from VCF files to CSV, TXT, JSON, HTML, SQLite, or terminal preview.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Getting Started with vcfzap
==========================

vcfzap is a versatile, open-source tool for extracting and processing contact information from VCF (vCard) files. It supports exporting to CSV, TXT, JSON, HTML, SQLite, or terminal preview, with features like filtering by name or phone number, encoding detection, and customizable output. For detailed documentation, source code, and community support, visit: https://github.com/mallikmusaddiq1/vcfzap.

Input Specifications
-------------------

• --search-name: Filter contacts by case-insensitive names, supporting Unicode, numbers, and symbols.
  Examples:
  $ vcfzap contacts.vcf --search-name "John Doe, Jane Smith"
  $ vcfzap contacts.vcf --search-name "Abc123, 😊, Elon Musk"

• --search-number: Filter contacts by phone numbers, supporting country codes and partial matches.
  Examples:
  $ vcfzap contacts.vcf --search-number "+1, 1234567890"
  $ vcfzap contacts.vcf --search-number "91, +12025550123"

• --fields: Specify fields to extract (comma-separated, case-insensitive).
  Valid fields: name, phone, email, address, organization
  Example:
  $ vcfzap contacts.vcf --csv output.csv --fields name,phone,email

Usage Examples
-------------

1. Preview the first 10 contacts in the terminal:
   $ vcfzap contacts.vcf --preview --limit 10
2. Export contacts to CSV with custom fields and delimiter:
   $ vcfzap contacts.vcf --csv contacts.csv --fields name,phone --csv-delimiter ";"
3. Filter by name and export to JSON with pretty-printing:
   $ vcfzap contacts.vcf --json contacts.json --search-name "Elon Musk, Jane Doe" --pretty-json
4. Export to SQLite with timestamped filename:
   $ vcfzap contacts.vcf --sqlite contacts.db --timestamp
5. Filter by phone number and preview in terminal:
   $ vcfzap contacts.vcf --preview --search-number "+1202, 1234567890"

For issues or feature requests, visit the GitHub repository: https://github.com/mallikmusaddiq1/vcfzap.
"""
    )
    parser.add_argument("vcf_file", help="Path to the input VCF file")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-c", "--csv", type=str, help="Export contacts as CSV file")
    output_group.add_argument("-t", "--txt", type=str, help="Export contacts as TXT file")
    output_group.add_argument("-j", "--json", type=str, help="Export contacts as JSON file")
    output_group.add_argument("-p", "--preview", action="store_true", help="Preview contacts in terminal")
    output_group.add_argument("-m", "--html", type=str, help="Export contacts as HTML file")
    output_group.add_argument("-s", "--sqlite", type=str, help="Export contacts to SQLite database")
    parser.add_argument("--limit", type=int, default=None, help="Limit output to first N contacts")
    parser.add_argument("--max-size", type=int, default=100, help="Warn if input file exceeds N MB")
    parser.add_argument("--no-color", action="store_true", help="Disable colored terminal output")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error console output")
    parser.add_argument("--timestamp", action="store_true", help="Append timestamp to output filenames")
    parser.add_argument("--detect-encoding", action="store_true", help="Detect file encoding")
    parser.add_argument("--csv-delimiter", type=str, default=",", help=f"Delimiter for CSV output (valid: {VALID_CSV_DELIMITERS})")
    parser.add_argument("--fields", type=str, default="name,phone,email", help=f"Fields to extract (e.g., {', '.join(VALID_FIELDS)})")
    parser.add_argument("--log-file", type=str, help="Save logs to specified file")
    parser.add_argument("--no-logs", action="store_true", help="Disable logging")
    parser.add_argument("--no-prompt", action="store_true", help="Skip interactive prompts")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--pretty-json", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--search-name", type=str, help="Filter contacts by names (comma-separated)")
    parser.add_argument("--search-number", type=str, help="Filter contacts by phone numbers (comma-separated)")
    parser.add_argument("--max-column-width", type=int, default=50, help="Maximum width for columns in preview table")
    parser.add_argument("-v", "--version", action="version", version=f"vcfzap {__version__}")
    args = parser.parse_args()

    logger = logging.getLogger('vcfzap')
    if args.no_logs and (args.verbose or args.quiet):
        cprint("Error: --no-logs cannot be used with --verbose or --quiet", "red", args.no_color, args.quiet)
        logger.error("Invalid argument combination: --no-logs with --verbose or --quiet")
        sys.exit(1)

    fields = [f.lower().strip() for f in args.fields.split(",") if f.strip()]
    if not fields:
        cprint(f"Error: No valid fields specified. Choose from: {', '.join(VALID_FIELDS)}", "red", args.no_color, args.quiet)
        logger.error("No valid fields specified")
        sys.exit(1)

    if args.search_name and "name" not in fields:
        cprint("Error: --search-name requires 'name' in --fields", "red", args.no_color, args.quiet)
        logger.error("--search-name used without 'name' in --fields")
        sys.exit(1)
    if args.search_number and "phone" not in fields:
        cprint("Error: --search-number requires 'phone' in --fields", "red", args.no_color, args.quiet)
        logger.error("--search-number used without 'phone' in --fields")
        sys.exit(1)

    search_names = [name.strip() for name in args.search_name.split(",") if name.strip()] if args.search_name else []
    search_numbers = [num.strip() for num in args.search_number.split(",") if num.strip()] if args.search_number else []

    if args.csv_delimiter not in VALID_CSV_DELIMITERS:
        cprint(f"Error: --csv-delimiter must be one of {VALID_CSV_DELIMITERS}", "red", args.no_color, args.quiet)
        logger.error(f"Invalid CSV delimiter: {args.csv_delimiter}")
        sys.exit(1)

    if args.max_column_width < 10:
        cprint("Error: --max-column-width must be at least 10", "red", args.no_color, args.quiet)
        logger.error(f"Invalid max-column-width: {args.max_column_width}")
        sys.exit(1)

    return argparse.Namespace(**vars(args), search_names=search_names, search_numbers=search_numbers)

def extract_contacts(
    vcf_path: Path, fields: List[str], detect_encoding: bool, no_color: bool, limit: Optional[int],
    quiet: bool, search_names: List[str], search_numbers: List[str]
) -> List[Dict[str, Any]]:
    """Extract specified fields from VCF file with streaming and filtering."""
    logger = logging.getLogger('vcfzap')
    contacts = []
    encoding = detect_file_encoding(vcf_path, no_color, quiet) if detect_encoding else DEFAULT_ENCODING
    logger.info(f"Extracting contacts from: {vcf_path}")

    encodings = [encoding] + [e for e in ["latin-1", "iso-8859-1", "windows-1252"] if e != encoding]
    contact_count = 0
    for enc in encodings:
        try:
            with vcf_path.open("r", encoding=enc, errors='replace') as f:
                vcard_stream = vobject.readComponents(f, allowQP=True)
                try:
                    name_patterns = [re.compile(re.escape(name), re.IGNORECASE | re.UNICODE) for name in search_names if name] if search_names else []
                    number_patterns = [re.compile(re.escape(num), re.IGNORECASE) for num in search_numbers if num] if search_numbers else []

                    for vcard in tqdm(islice(vcard_stream, limit), total=limit, desc="Parsing contacts", disable=no_color or quiet or limit is None):
                        try:
                            contact = {}
                            if "name" in fields:
                                fn = getattr(vcard, 'fn', None)
                                contact["name"] = normalize_value(fn.value if fn else None) or ""
                                if name_patterns and not any(pattern.search(contact["name"]) for pattern in name_patterns):
                                    continue

                            if "phone" in fields:
                                phones = [clean_phone_number(tel.value) for tel in getattr(vcard, 'tel_list', []) if tel.value]
                                contact["phone"] = ", ".join(phones) if phones else ""
                                if number_patterns and phones and not any(any(pattern.search(phone) for pattern in number_patterns) for phone in phones):
                                    continue

                            if "email" in fields:
                                emails = [email.value for email in getattr(vcard, 'email_list', []) if email.value]
                                contact["email"] = ", ".join(emails) if emails else ""

                            if "address" in fields:
                                addresses = [format_address(adr) for adr in getattr(vcard, 'adr_list', []) if adr.value]
                                contact["address"] = ", ".join(addresses) if addresses else ""

                            if "organization" in fields:
                                org_list = getattr(vcard, 'org_list', [])
                                organizations = [
                                    normalize_value(org.value[0] if isinstance(org.value, list) and org.value else org.value)
                                    for org in org_list if org.value
                                ]
                                contact["organization"] = ", ".join(organizations) if organizations else ""

                            if any(contact.values()):
                                contacts.append(contact)
                                contact_count += 1
                        except Exception as e:
                            logger.warning(f"Skipping invalid vCard: {e}")
                            continue
                    if contact_count > 0:
                        if enc != encoding:
                            cprint(f"Warning: Used fallback encoding '{enc}' instead of detected '{encoding}'", "yellow", no_color, quiet)
                            logger.warning(f"Used fallback encoding '{enc}' instead of detected '{encoding}'")
                        break
                except vobject.base.ParseError as e:
                    cprint(f"Error: Failed to parse VCF: {e}. Ensure proper vCard formatting", "red", no_color, quiet)
                    logger.error(f"Failed to parse VCF: {e}")
                    sys.exit(1)
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode with encoding: {enc}")
            continue
        except IOError as e:
            cprint(f"Error reading VCF file: {e}", "red", no_color, quiet)
            logger.error(f"Failed to read VCF file '{vcf_path}': {e}")
            sys.exit(1)

    if not contacts:
        message = "No valid contacts found" + (
            f" matching name filters '{', '.join(search_names)}' and number filters '{', '.join(search_numbers)}'"
            if search_names and search_numbers else
            f" matching name filters '{', '.join(search_names)}'" if search_names else
            f" matching number filters '{', '.join(search_numbers)}'" if search_numbers else ""
        )
        cprint(message, "yellow", no_color, quiet)
        logger.info(message)
    else:
        logger.info(f"Extracted {contact_count} contacts")
    return contacts

def format_filename(base: str, ext: str, use_timestamp: bool) -> Path:
    """Format output filename with optional timestamp."""
    if not base.endswith(f".{ext}"):
        base = f"{base}.{ext}"
    if use_timestamp:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{base.rsplit('.', 1)[0]}_{timestamp}.{ext}"
    return Path(base).resolve()

def write_file(
    filepath: Path, contacts: List[Dict[str, Any]], format_type: str, fields: List[str],
    no_color: bool, quiet: bool, csv_delimiter: str, pretty_json: bool
) -> None:
    """Write contacts to file in specified format."""
    logger = logging.getLogger('vcfzap')
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        if format_type == "csv":
            write_csv(filepath, contacts, csv_delimiter, no_color, quiet)
        elif format_type == "txt":
            write_txt(filepath, contacts, no_color, quiet)
        elif format_type == "json":
            write_json(filepath, contacts, pretty_json, no_color, quiet)
        elif format_type == "html":
            write_html_file(filepath, contacts, no_color, quiet)
        elif format_type == "sqlite":
            write_sqlite(filepath, contacts, fields, no_color, quiet)
        if contacts:
            cprint(f"✓ {format_type.upper()} saved: {filepath}", "green", no_color, quiet)
    except (PermissionError, IOError, sqlite3.Error) as e:
        cprint(f"Error writing {format_type.upper()} file: {e}", "red", no_color, quiet)
        logger.error(f"Failed to write {format_type.upper()} to '{filepath}': {e}")
        sys.exit(1)

def validate_fields(fields: List[str], no_color: bool, quiet: bool) -> List[str]:
    """Validate and deduplicate fields."""
    logger = logging.getLogger('vcfzap')
    cleaned_fields = list(dict.fromkeys(f.lower().strip() for f in fields if f.strip()))
    invalid_fields = [f for f in cleaned_fields if f not in VALID_FIELDS]
    if invalid_fields:
        cprint(f"Error: Invalid fields: {', '.join(invalid_fields)}. Choose from: {', '.join(VALID_FIELDS)}", "red", no_color, quiet)
        logger.error(f"Invalid fields specified: {', '.join(invalid_fields)}")
        sys.exit(1)
    if not cleaned_fields:
        cprint(f"Error: No valid fields specified. Choose from: {', '.join(VALID_FIELDS)}", "red", no_color, quiet)
        logger.error("No valid fields specified")
        sys.exit(1)
    logger.debug(f"Validated fields: {', '.join(cleaned_fields)}")
    return cleaned_fields

def main() -> None:
    """Main function to orchestrate VCF contact extraction."""
    logger = logging.getLogger('vcfzap')
    logger.info("Starting vcfzap execution")
    args = parse_arguments()

    setup_logging(args.log_file, args.no_logs, args.verbose)
    fields = validate_fields(args.fields.split(","), args.no_color, args.quiet)

    if args.limit is not None and args.limit <= 0:
        cprint("Error: --limit must be a positive integer", "red", args.no_color, args.quiet)
        logger.error(f"Invalid limit value: {args.limit}")
        sys.exit(1)

    if not (args.csv or args.txt or args.json or args.preview or args.html or args.sqlite):
        cprint("Error: Must specify an output method: --csv, --txt, --json, --html, --sqlite, or --preview. Use --help for usage information.", "red", args.no_color, args.quiet)
        logger.error("No output method specified")
        sys.exit(1)

    if not args.vcf_file:
        cprint("Error: VCF file path is required", "red", args.no_color, args.quiet)
        logger.error("No VCF file path provided")
        sys.exit(1)

    output_paths = {}
    for ext, filename in [("csv", args.csv), ("txt", args.txt), ("json", args.json), ("html", args.html), ("sqlite", args.sqlite)]:
        if filename:
            output_paths[ext] = validate_file(
                format_filename(filename, "db" if ext == "sqlite" else ext, args.timestamp),
                "db" if ext == "sqlite" else ext, False, args.max_size, args.no_color, args.quiet, args.no_prompt
            )

    contacts = extract_contacts(
        validate_file(args.vcf_file, "vcf", True, args.max_size, args.no_color, args.quiet, args.no_prompt),
        fields, args.detect_encoding, args.no_color, args.limit, args.quiet, args.search_names, args.search_numbers
    )

    if args.preview:
        cprint(f"Previewing {len(contacts)} contacts", "blue", args.no_color, args.quiet)
        preview_contacts(contacts, args.no_color, args.quiet, args.max_column_width)

    for ext, path in output_paths.items():
        write_file(path, contacts, ext, fields, args.no_color, args.quiet, args.csv_delimiter, args.pretty_json)

    logger.info("Execution completed successfully")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("Operation interrupted by user", "red", False, False)
        logging.getLogger('vcfzap').info("Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        cprint(f"Error: Unexpected issue occurred: {e}", "red", False, False)
        logging.getLogger('vcfzap').error(f"Unexpected error: {e}")
        sys.exit(1)