# Usage Guide

## Basic Commands

### Single Compound
```bash
./molecule-scraper -c "Caffeine" -o caffeine_data.csv
```

### Multiple Compounds
```bash
./molecule-scraper -c "Caffeine" "Aspirin" "Ibuprofen" -o drugs.csv
```

### From File
```bash
./molecule-scraper -f compounds.txt -o results.csv
```

## Input Formats

### Command Line
- Use quotes for compound names with spaces
- Separate multiple compounds with spaces

### File Input
- One compound name per line
- Supports .txt and .json formats
- JSON format: `{"compounds": ["Caffeine", "Aspirin"]}`

## Output Format

Results are saved as CSV with these columns:
- **Chemical Species**: IUPAC name
- **Chemical Name**: Common name
- **Chemical Formula**: Molecular formula
- **CAS#**: Chemical Abstracts Service number
- **Properties**: Physical and chemical properties
- **MSDS**: Safety and hazard information

## Advanced Options

```bash
# Custom output filename
./molecule-scraper -c "Caffeine" -o custom_name.csv

# Adjust API delay (be respectful)
./molecule-scraper -c "Caffeine" --delay 2.0

# Verbose output
./molecule-scraper -c "Caffeine" --verbose
```

## Tips

1. **Large lists**: For 100+ compounds, use file input
2. **Rate limiting**: Tool includes automatic delays
3. **Error handling**: Failed compounds are logged
4. **CSV format**: Compatible with Excel, Google Sheets