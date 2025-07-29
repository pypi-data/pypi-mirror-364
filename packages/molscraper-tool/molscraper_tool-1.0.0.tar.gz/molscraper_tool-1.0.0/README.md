# Molscraper

[![PyPI version](https://badge.fury.io/py/molscraper.svg)](https://badge.fury.io/py/molscraper)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Chemical data extraction tool for researchers, students, and industry professionals.

## 🧪 What is Molscraper?

Molscraper is a comprehensive Python tool that extracts detailed chemical compound information from PubChem's REST API. Transform chemical compound names into structured datasets containing molecular properties, safety information, applications, and more.

## ✨ Key Features

- **🎯 Advanced CAS Number Extraction** - Multiple extraction strategies with automatic fallbacks
- **📋 Comprehensive Data Extraction** - 11 standardized data fields per compound
- **🔒 Advanced Safety Data** - MSDS information and hazard classifications  
- **⚡ High Performance** - Smart rate limiting and efficient API usage
- **🐍 Python Integration** - Use as CLI tool or import as Python library
- **📊 Research Ready** - Outputs to CSV for immediate analysis
- **🔍 Smart Recognition** - Functional group identification and applications

## 🚀 Quick Installation

Install from PyPI (recommended):

```bash
pip install molscraper
```

## 🚀 Quick Start

### Installation
```bash
pip install molscraper
```

### Command Line Interface

```bash
# Extract data for specific compounds
molscraper -c "Benzaldehyde" "Caffeine" "Aspirin"

# From text file (one compound per line)
molscraper -f examples/compounds.txt

# From CSV (auto-detects compound column)
molscraper -f examples/research_data.csv -o results.csv

# From Excel file  
molscraper -f examples/compound_list.xlsx --verbose

# Custom settings
molscraper -f my_data.csv --delay 0.5 --verbose
```

### File Input Support

```bash
# Text files - one compound per line
molscraper -f compounds.txt

# CSV files - auto-detects compound columns
molscraper -f research_data.csv

# Excel files (.xlsx) 
molscraper -f lab_compounds.xlsx

# JSON files
molscraper -f compound_list.json

# CSV with different separators
molscraper -f messy_data.csv
```

**Note:** For best results, name your CSV column "compound" or "chemical", though other column names are automatically detected.

### Python API

```python
from molecule_scraper import process_compounds_to_csv, PubChemScraper

# Quick extraction to CSV
compounds = ["Benzaldehyde", "Caffeine", "Aspirin"]
df = process_compounds_to_csv(compounds, 'results.csv')

# Advanced usage with custom scraper
scraper = PubChemScraper(delay=0.3)
data = scraper.get_compound_data("Morphine")
print(f"CAS Number: {data.cas_number}")
print(f"Formula: {data.chemical_formula}")
```

## 📊 Data Fields Extracted

| Field | Description |
|-------|-------------|
| Chemical Species | IUPAC name |
| Functional Group | Applications and uses |
| Chemical Name | Common name |
| Chemical Formula | Molecular formula |
| Structural Formula | SMILES notation |
| Extended SMILES | Canonical SMILES |
| CAS# | Chemical registry number |
| Properties | Physical properties |
| Applications | Commercial uses |
| MSDS | Safety data |
| Hazard Information | Safety classifications |

## 🎯 Perfect for Chemists

**Computational Chemists:**
- Integrates seamlessly with existing Python workflows
- Works in Jupyter notebooks
- Compatible with pandas, numpy, matplotlib
- Easy to include in `requirements.txt`

**Academic Researchers:**
- Reproducible research workflows
- Batch processing capabilities
- Publication-ready data formats

**Industry Professionals:**
- High-throughput compound analysis
- Automated safety data collection
- Integration with existing systems

## 📁 Input Formats

### 📄 Text Files (`.txt`)
```
Benzaldehyde
Caffeine
Aspirin
```

### 📊 CSV Files (`.csv`) - Auto-detects compound columns!
```csv
compound,category,priority
Aspirin,NSAID,High
Caffeine,Stimulant,Medium
Ibuprofen,NSAID,High
```

**Supported column names:** `compound`, `chemical`, `molecule`, `name`, `substance`, and others.
**Supported separators:** Commas, semicolons, tabs.

### 📊 Excel Files (`.xlsx`)
Just save your spreadsheet as Excel format - same auto-detection as CSV!

### 📋 JSON Files (`.json`)
```json
{
  "compounds": ["Benzaldehyde", "Caffeine", "Aspirin"],
  "description": "Test compounds for analysis"
}
```

### 🔧 Data Format Support
The parser handles:
- Different separators (`,` `;` `\t`)
- Various encodings (UTF-8, Latin1, etc.)
- Headers and metadata
- Quoted fields
- Empty rows

**Note:** Most standard data files work without reformatting.

## 🎯 Try Our Examples!

We've included ready-to-use example files:

```bash
# 🧪 Basic pharmaceutical compounds
molscraper -f examples/sample_compounds.txt

# 🔬 Research lignans and flavonoids  
molscraper -f examples/research_data.csv --verbose

# 💊 Drug discovery compounds
molscraper -f examples/drug_discovery.csv

# 🌿 Natural products from traditional medicine
molscraper -f examples/natural_products.csv

# 📊 Excel file with therapeutic classifications
molscraper -f examples/compound_list.xlsx

# 📋 JSON format research compounds
molscraper -f examples/research_compounds.json
```

📚 **New to molscraper?** Check out our [complete tutorial](examples/tutorials/getting_started.md)!

## 🛠️ Advanced Usage

### CLI Options

```bash
molscraper --help

Options:
  -c, --compounds TEXT         Compound names (space-separated)
  -f, --file PATH             Input file (.txt or .json)
  -o, --output PATH           Output CSV file
  --delay FLOAT               Delay between requests (default: 0.2)
  --verbose                   Enable detailed logging
  --help                      Show this message and exit
```

### Error Handling

The tool includes comprehensive error handling:
- Network timeouts and retries
- Invalid compound name detection
- API rate limit management
- Graceful degradation for partial data

## 🔬 Why Choose Molscraper?

### vs. Manual PubChem Searches
- **Automated batch processing** vs manual lookup
- **Consistent formatting** across all compounds
- **Batch processing** capabilities
- **Automated CAS number extraction**

### vs. Other Chemical APIs
- **No API keys required** - uses free PubChem REST API
- **Advanced data extraction** - gets safety and application data
- **Robust CAS extraction** - multiple strategies with automatic fallbacks
- **Ready-to-use** - no complex setup

### vs. Basic Scripts
- **Robust error handling** - network timeouts and retries
- **Rate limiting** - respects API limits
- **Comprehensive data** - extracts 11+ data fields
- **Structured output** - standardized CSV format

## 📚 Examples

See the `examples/` directory for:
- `compounds.txt` - Basic compound list
- `research_compounds.json` - Research-focused compounds
- `sample_output.csv` - Example results

## 🤝 Contributing

For product feedback, feature requests, or questions, please reach out to: **x@rhizome-research.com**

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: This README and inline code docs
- **Contact**: Send questions or feedback to x@rhizome-research.com
- **Examples**: Check the `examples/` directory

---

**Quick Start:**

```bash
pip install molscraper
molscraper -c "Caffeine" -o test.csv
``` 