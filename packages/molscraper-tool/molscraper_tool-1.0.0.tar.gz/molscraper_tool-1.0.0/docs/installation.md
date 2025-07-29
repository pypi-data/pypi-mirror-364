# Installation Guide

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Architecture**: x64 (Intel/AMD) or ARM64 (Apple Silicon)
- **Memory**: 100MB available space
- **Network**: Internet connection for data retrieval

## Download

1. Go to [Releases page](https://github.com/yourusername/molecule-scraper/releases/latest)
2. Download the appropriate version for your platform
3. Follow platform-specific instructions below

### Windows
1. Download `molecule-scraper-windows.exe`
2. Run directly from command prompt or PowerShell

### macOS
1. Download appropriate version:
   - Apple Silicon (M1/M2/M3): `molecule-scraper-macos-arm64`
   - Intel: `molecule-scraper-macos-x64`
2. Make executable: `chmod +x molecule-scraper-*`
3. Run: `./molecule-scraper-macos-arm64`

### Linux
1. Download `molecule-scraper-linux`
2. Make executable: `chmod +x molecule-scraper-linux`
3. Run: `./molecule-scraper-linux`

## Verification

Test your installation:
```bash
./molecule-scraper -c "Water" -o test.csv
```

You should see output like:
```
Success! Processed 1 compounds.
Results saved to test.csv
```