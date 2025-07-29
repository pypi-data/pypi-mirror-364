# Getting Started with Molecule Scraper

This tutorial shows you all the different ways to use molecule-scraper to extract chemical data.

## 🚀 Quick Start

### Method 1: Direct Command Line Input
```bash
# Process specific compounds directly
molecule-scraper -c "Aspirin" "Caffeine" "Ibuprofen"

# With custom output file
molecule-scraper -c "Water" "Ethanol" -o my_results.csv
```

### Method 2: Text File Input (.txt)
```bash
# Create a simple text file with compound names (one per line)
# File: my_compounds.txt
echo -e "Benzaldehyde\nVanillin\nMenthol" > my_compounds.txt

# Process the file
molecule-scraper -f my_compounds.txt -o results.csv
```

### Method 3: CSV File Input (.csv)
```bash
# Works with any CSV that has compound names
# The tool automatically detects the compound column!

# Try our research data example
molecule-scraper -f examples/research_data.csv -o research_results.csv

# Or drug discovery data
molecule-scraper -f examples/drug_discovery.csv -o drug_results.csv

# Even messy data with tab separators
molecule-scraper -f examples/messy_data.csv -o clean_results.csv
```

### Method 4: Excel File Input (.xlsx)
```bash
# Works with Excel files too!
molecule-scraper -f examples/compound_list.xlsx -o excel_results.csv
```

### Method 5: JSON Input (.json)
```bash
# Process structured JSON data
molecule-scraper -f examples/research_compounds.json -o json_results.csv
```

## 🔧 Advanced Options

### Control Processing Speed
```bash
# Faster processing (be respectful to PubChem!)
molecule-scraper -f my_compounds.txt --delay 0.5

# Slower, more conservative
molecule-scraper -f my_compounds.txt --delay 2.0
```

### Verbose Output
```bash
# See detailed processing information
molecule-scraper -f my_compounds.txt --verbose
```

### Complete Example
```bash
# Process natural products with verbose logging and custom delay
molecule-scraper -f examples/natural_products.csv -o natural_results.csv --delay 0.8 --verbose
```

## 📊 Input File Formats

### Text Files (.txt)
```
Aspirin
Caffeine
Ibuprofen
```

### CSV Files (.csv)
The tool automatically detects compound columns! Name your column any of these for best results:
- `compound` or `compounds`
- `chemical` or `chemicals` 
- `molecule` or `molecules`
- `name` or `names`
- `substance`

Example CSV:
```csv
compound,category,notes
Aspirin,NSAID,Pain reliever
Caffeine,Stimulant,Found in coffee
```

### Excel Files (.xlsx)
Same as CSV - just save your spreadsheet as Excel format. Works with multiple sheets (uses first sheet).

### JSON Files (.json)
```json
{
  "compounds": ["Aspirin", "Caffeine", "Ibuprofen"],
  "category": "Common drugs"
}
```

Or simple list:
```json
["Aspirin", "Caffeine", "Ibuprofen"]
```

## 🎯 What You Get

Each compound is processed to extract:
- ✅ **Chemical Name** - IUPAC and common names
- ✅ **Chemical Formula** - Molecular formula  
- ✅ **CAS Number** - Chemical Abstract Service number
- ✅ **SMILES** - Structural representation
- ✅ **Properties** - Physical and chemical properties
- ✅ **Applications** - Uses and applications
- ✅ **MSDS Data** - Safety and hazard information
- ✅ **Functional Groups** - Chemical classifications

## 🔍 Example Output

```csv
Chemical Name,Chemical Formula,CAS#,Properties,Applications
Aspirin,C9H8O4,50-78-2,"MW: 180.16, MP: 135°C","Pain relief, Anti-inflammatory"
Caffeine,C8H10N4O2,58-08-2,"MW: 194.19, MP: 235°C","Stimulant, Beverage additive"
```

## 💡 Pro Tips

1. **Name your CSV columns clearly** - Use "compound" or "chemical" for best auto-detection
2. **Start small** - Test with a few compounds first
3. **Use appropriate delays** - Default 1.0 seconds is usually good
4. **Check your results** - Review the output CSV for any missing data
5. **Use verbose mode** - `--verbose` shows you exactly what's happening

## 🔧 Troubleshooting

### "No compounds found"
- Check your file format
- Make sure compound names are in the first column or a clearly named column
- Try renaming your column to "compound"

### "File parsing failed"
- Try saving your file as UTF-8 encoding
- Check for special characters
- Try a different file format (Excel → CSV)

### "API errors"
- Increase the delay with `--delay 2.0`
- Check your internet connection
- Some compound names might not exist in PubChem

## 🎓 Ready to Try?

Start with our example files:
```bash
# Basic compounds
molecule-scraper -f examples/sample_compounds.txt

# Research data with categories
molecule-scraper -f examples/research_data.csv --verbose

# Natural products
molecule-scraper -f examples/natural_products.csv

# Excel example
molecule-scraper -f examples/compound_list.xlsx
```

Happy molecule scraping! 🧪 