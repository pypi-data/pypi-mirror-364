![License](https://img.shields.io/github/license/mallikmusaddiq1/vcfzap)
![Python Version](https://img.shields.io/pypi/pyversions/vcfzap)
![Stars](https://img.shields.io/github/stars/mallikmusaddiq1/vcfzap)
![Last Commit](https://img.shields.io/github/last-commit/mallikmusaddiq1/vcfzap)
![Code Size](https://img.shields.io/github/languages/code-size/mallikmusaddiq1/vcfzap)
![Top Language](https://img.shields.io/github/languages/top/mallikmusaddiq1/vcfzap)

# vcfzap

**vcfzap** is a high-performance, feature-rich command-line tool that extracts contact information from VCF (vCard) files and exports it into multiple formats: CSV, TXT, JSON, HTML, SQLite, or a color-coded terminal preview. Whether you're a developer, sysadmin, or power user, vcfzap makes contact extraction seamless and efficient.

---

## ✨ Key Features

* 🚀 **Multi-format Export**: Convert `.vcf` files to CSV, TXT, JSON, HTML, or SQLite database.
* 🧩 **Field Selection**: Choose exactly which fields to extract: name, phone, email, address, organization.
* 🔍 **Dry Run Mode**: Simulate output without creating any files — perfect for testing.
* 🌐 **Encoding Detection**: Automatically handles VCFs with different character encodings.
* 🔐 **Safe Overwriting**: Built-in prompts to prevent accidental file overwrite and respect for permissions.
* ⚡ **Performance-focused**: Fast parsing with progress display — handles large files effortlessly.
* ⌚ **Timestamp Support**: Automatically append timestamps to output filenames.
* 🧘 **Automation-friendly**: Flags like `--no-color`, `--quiet`, and `--no-prompt` are ideal for scripting and CI.
* 💽 **Rich Terminal Preview**: View a beautiful table-rendered contact list directly in the terminal.
* 🛠 **Verbose Logging**: Output logs to file and optionally enable debug mode for advanced insight.

---

## ⚙ Installation

### 📦 Install via PyPI

```bash
pip install vcfzap
```

### 🧬 Install from GitHub (latest)

```bash
git clone https://github.com/musaddiq/vcfzap.git
cd vcfzap
pip install .
```

---

## 🧪 Basic Usage

```bash
vcfzap <VCF_FILE> [OPTIONS]
```

### ✅ Examples

```bash
vcfzap contacts.vcf --preview --limit 5
vcfzap contacts.vcf --csv output.csv --timestamp
vcfzap contacts.vcf --json contacts.json --fields name,phone,email --pretty-json
vcfzap contacts.vcf --html contacts.html --fields email
vcfzap contacts.vcf --sqlite contacts.db --no-prompt
vcfzap --check-dependencies
```

---

## ⚙ Options & Arguments

### 📅 Input

* `vcf_file` (positional): Path to your `.vcf` file.

### 🎯 Output Formats *(choose one)*

* `--csv <file>`: Export to CSV file
* `--txt <file>`: Export to plain text file
* `--json <file>`: Export to JSON file
* `--html <file>`: Export to styled HTML table
* `--sqlite <file>`: Export to SQLite database
* `--preview`: Show contacts in a color-coded terminal table (no file output)

### 🎛 Behavior & Customization

* `--fields name,phone,email`: Comma-separated list of fields to extract
* `--limit N`: Limit number of contacts
* `--timestamp`: Add current timestamp to output filename
* `--max-size N`: Warn if file is larger than N MB
* `--detect-encoding`: Automatically detect file encoding
* `--csv-delimiter ";"`: Set custom delimiter for CSV export
* `--log-file <file>`: Save detailed logs to specified file
* `--no-color`: Disable colored CLI output
* `--quiet`: Suppress non-essential messages
* `--no-logs`: Disable logging entirely
* `--no-prompt`: Disable all interactive prompts (force overwrite, large file warning)
* `--pretty-json`: Enable human-readable indented JSON
* `--check-dependencies`: Check for any missing Python dependencies
* `-v`, `--version`: Show version information

---

## 🌐 Field Reference

| Field          | Description                            |
| -------------- | -------------------------------------- |
| `name`         | Full name (e.g., John Doe)             |
| `phone`        | Phone numbers with optional extensions |
| `email`        | Email addresses                        |
| `address`      | Full physical address                  |
| `organization` | Company or organization name           |

---

## 📦 Output Format Overview

| Format  | Description                               |
| ------- | ----------------------------------------- |
| CSV     | Clean spreadsheet with optional delimiter |
| TXT     | Readable text with labeled fields         |
| JSON    | Compact or pretty-printed structure       |
| HTML    | Styled responsive HTML table              |
| SQLite  | Structured database with dynamic schema   |
| Preview | Terminal-based color table preview only   |

---

## ❗ Notes

* Only one output format can be specified per command.
* Use `--dry-run` to verify before exporting.
* Ideal for automation pipelines via `--no-prompt`, `--quiet`, and `--log-file`.

---

## 🧑‍💻 Advanced Usage

```bash
vcfzap mycontacts.vcf \
  --csv contacts.csv \
  --fields name,email,address \
  --timestamp \
  --detect-encoding \
  --log-file logs/vcfzap.log \
  --quiet
```

---

## 🛡 License

MIT License
---

## 👨‍💻 Author

**Crafted with intent by [Mallik Mohammad Musaddiq](https://github.com/musaddiqmalik)**
**📧 [musaddiqmalik@gmail.com](mailto:musaddiqmalik@gmail.com)**
**🔗 [GitHub Repo](https://github.com/mallikmusaddiq1/vcfzap)**

---

## 🔍 Like vcfzap?

If this tool made your workflow easier, consider ⭐️ starring the repository or sharing it with others in need.
*
**📧 [musaddiqmalik@gmail.com](mailto:musaddiqmalik@gmail.com)**
**🔗 [GitHub Repo](https://github.com/mallikmusaddiq1/vcfzap)**

---

## 🔍 Like vcfzap?

If this tool made your workflow easier, consider ⭐️ starring the repository or sharing it with others in need.
