# 🕵️ Anon - Privacy-First Text Anonymizer

[![CI](https://github.com/ATirelli/anonymizer/actions/workflows/ci.yml/badge.svg)](https://github.com/ATirelli/anonymizer/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/simple-anonymizer.svg)](https://pypi.org/project/simple-anonymizer/)
[![Python Version](https://img.shields.io/pypi/pyversions/simple-anonymizer.svg)](https://pypi.org/project/simple-anonymizer/)


A powerful, **offline-first** text anonymization tool that removes personal identifiable information (PII) from text while keeping all data on your machine. Built with enterprise-grade accuracy using spaCy NER models and Microsoft Presidio.

## ✨ Features

- 🔒 **100% Offline** - All processing happens on your machine
- 🎯 **High Accuracy** - Advanced NER using spaCy large models + Presidio
- 🔐 **Secure Always-Redact** - Custom sensitive terms stored securely in `~/.anonymizer`
- 🖥️ **Multiple Interfaces** - Modern GUI, Web API, and CLI
- 🚀 **Background Processing** - CLIs run detached with proper logging
- 📦 **Easy Installation** - One-command install with automatic model setup
- 🏢 **Cross-Platform** - Windows, macOS, and Linux support

## 🚀 Quick Start

### Installation

```bash
pip install simple-anonymizer
```

The installation will automatically download the required spaCy model (`en_core_web_lg`) for optimal accuracy.

### Model Setup

After installation, you may need to set up the required spaCy models for full functionality:

```bash
# Automatic setup (recommended)
anon-setup-models
```

This will install:
- `en_core_web_lg` - Primary model for high-accuracy PII detection
- `en_core_web_sm` - Compatibility model for text-anonymizer integration

**Manual Installation** (if automatic setup fails):
```bash
# Primary model (large, best accuracy)
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl

# Compatibility model (small, for text-anonymizer)
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

**Corporate Networks** (if SSL certificate issues occur):
```bash
pip install --trusted-host github.com --trusted-host objects.githubusercontent.com https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
```

ℹ️ **Note**: The anonymizer will work with pattern-based detection and always-redact functionality even without the spaCy models, but accuracy will be reduced.

### GUI Application

Launch the modern GUI interface:

```bash
anon-gui
```

✅ **The GUI runs in background** - you can close the terminal after launch

📝 **Logs available** at `~/.anonymizer/gui_YYYYMMDD_HHMMSS.log`

### Web Interface

Start the web server:

```bash
anon-web start
```

✅ **Server runs in background** - accessible at http://127.0.0.1:8080

📝 **Comprehensive logging** and process management

#### Web Server Management

```bash
# Start server (custom host/port)
anon-web start --host 0.0.0.0 --port 5000

# Check server status
anon-web status

# View recent logs
anon-web logs

# Stop server
anon-web stop

# Clean old log files (preserves always-redact settings)
anon-web clean
```

### Always-Redact Management

Securely manage custom sensitive terms that should always be anonymized:

```bash
# Add terms to always-redact list
anon-web add-redact "CompanyName"
anon-web add-redact "ProjectCodename"

# Remove terms from always-redact list
anon-web remove-redact "ProjectCodename"

# List all always-redacted terms
anon-web list-redact
```

🔐 **Security Features:**
- Terms stored securely in `~/.anonymizer/always_redact.txt`
- Not visible in GUI or web interfaces (add/remove only)
- Persists across all anonymization operations
- Case-insensitive matching with duplicate prevention

### Python API

```python
from anonymizer_core import redact

# Basic anonymization
result = redact("John Doe works at Microsoft in Seattle.")
print(result.text)
# Output: "<REDACTED> works at <REDACTED> in <REDACTED>."

# Always-redact terms are automatically applied
# (managed via CLI commands shown above)
result = redact("Contact john@acme.com about AcmeProject details.")
print(result.text)
# Output: "Contact <REDACTED> about <REDACTED> details."
# (if "AcmeProject" was added to always-redact list)
```

## 🔐 Data Security & Privacy

### Always-Redact Terms
- **Secure Storage**: Custom sensitive terms are stored in `~/.anonymizer/always_redact.txt`
- **No Shipping**: The file is created locally on first use, never shipped with the package
- **Privacy-First**: Terms are not exposed through GUI or web interfaces
- **CLI-Only Access**: Terms can only be viewed via command line for security
- **Persistent**: Settings survive application updates and log cleanups

### File Locations
```bash
# User data directory
~/.anonymizer/
├── always_redact.txt         # Your custom sensitive terms
├── gui_YYYYMMDD_HHMMSS.log  # GUI application logs
└── web_server_*.log         # Web server logs
```

### Data Flow
1. **Input Text** → **Standard PII Detection** (emails, phones, etc.)
2. **Input Text** → **Always-Redact Terms** (your custom words) 
3. **Combined Results** → **Final Anonymized Output**

## 🔧 Advanced Usage

### GUI Features
- **Modern Interface**: Clean, intuitive design with real-time processing
- **Secure Term Management**: Add/remove always-redact terms without exposure
- **File Processing**: Load and save text files directly
- **Background Processing**: Non-blocking anonymization with progress indicators

### Web API Features
- **RESTful Endpoints**: Standard HTTP API for integration
- **File Upload**: Process text files via web interface  
- **JSON Response**: Structured output with metadata
- **Health Checks**: Monitor service status programmatically

### CLI Management
- **Process Control**: Start/stop/status for web server
- **Log Management**: View and clean application logs
- **Term Management**: Secure always-redact term administration
- **Background Operation**: All services run detached from terminal

## 🛠️ Technical Details

### Anonymization Engine
- **Multi-Tier Processing**: Pattern-based → Always-redact → NER fallback
- **Position Tracking**: Prevents overlapping redactions for accuracy
- **Case Insensitive**: Always-redact terms match regardless of case
- **Word Boundaries**: Only complete words are redacted (not partial matches)

### Supported Entity Types
- **Emails**: john@example.com
- **URLs**: https://example.com  
- **IP Addresses**: 192.168.1.1
- **Phone Numbers**: +1-555-123-4567
- **Custom Terms**: Your always-redact list
- **Names**: Via NER when available
- **Organizations**: Via NER when available

## 📋 Examples & Use Cases

### Basic Anonymization
```python
from anonymizer_core import redact

text = "Please contact John Smith at john.smith@acme.com or call +1-555-0123."
result = redact(text)
print(result.text)
# Output: "Please contact <REDACTED> at <REDACTED> or call <REDACTED>."
```

### Company-Specific Anonymization
```bash
# Set up company-specific terms
anon-web add-redact "AcmeCorp"
anon-web add-redact "ProjectTitan"
anon-web add-redact "confidential"

# Now these terms are always redacted
python -c "
from anonymizer_core import redact
text = 'AcmeCorp confidential: ProjectTitan budget is 500K'
print(redact(text).text)
"
# Output: "<REDACTED> <REDACTED>: <REDACTED> budget is 500K"
```

### Enterprise Integration
```python
# Configure once via CLI
# anon-web add-redact "YourCompanyName"
# anon-web add-redact "YourProduct"

# Use in your application
from anonymizer_core import redact

def process_support_ticket(ticket_text):
    """Anonymize support tickets before logging."""
    result = redact(ticket_text)
    return result.text

# All company-specific terms are automatically redacted
anonymized = process_support_ticket(
    "Customer john@email.com reported YourProduct crashed on YourCompanyName servers."
)
print(anonymized)
# Output: "Customer <REDACTED> reported <REDACTED> crashed on <REDACTED> servers."
```

### Batch Processing
```bash
# Set up your terms once
anon-web add-redact "SensitiveTerm1"
anon-web add-redact "SensitiveTerm2"

# Process multiple files - terms persist across all operations
for file in *.txt; do
    python -c "
from anonymizer_core import redact
with open('$file', 'r') as f:
    content = f.read()
with open('anonymized_$file', 'w') as f:
    f.write(redact(content).text)
    "
done
```

### Security Audit
```bash
# List all configured terms (CLI only for security)
anon-web list-redact

# Remove terms that are no longer sensitive
anon-web remove-redact "OldProjectName"

# Clean logs while preserving term configuration
anon-web clean
```

## 🚨 Security Best Practices

### Always-Redact Configuration
- **Review Regularly**: Audit your always-redact terms periodically
- **Principle of Least Privilege**: Only add terms that truly need redaction
- **Team Coordination**: Ensure team members know which terms are configured
- **Backup**: Consider backing up `~/.anonymizer/always_redact.txt` securely

### Production Deployment
- **Isolated Environment**: Deploy in secure, isolated environments
- **Log Management**: Regularly clean logs with `anon-web clean`
- **Access Control**: Restrict CLI access to authorized personnel only
- **Monitor Usage**: Review anonymization logs for compliance

## 📊 CLI Command Reference

### Server Management
```bash
anon-web start [--host HOST] [--port PORT]  # Start web server
anon-web stop                                # Stop web server  
anon-web status                              # Check server status
anon-web logs                                # View recent logs
anon-web clean                               # Clean old logs (preserve settings)
```

### Always-Redact Management
```bash
anon-web add-redact "TERM"                   # Add term to always-redact list
anon-web remove-redact "TERM"                # Remove term from list
anon-web list-redact                         # List all terms (CLI only)
```

### GUI Launch
```bash
anon-gui                                     # Launch GUI application
```

## 🔍 Troubleshooting

### Common Issues

**Terms not being redacted?**
- Verify term was added: `anon-web list-redact`
- Check exact spelling and case sensitivity
- Ensure word boundaries (partial matches won't work)

**GUI/Web not reflecting new terms?**
- This is by design for security
- Terms are automatically applied during anonymization
- Use CLI `list-redact` to verify configuration

**Server won't start?**
- Check if port is already in use: `anon-web status`
- Try different port: `anon-web start --port 8081`
- Check logs: `anon-web logs`

**Performance issues?**
- Clean old logs: `anon-web clean`
- For large texts, consider batch processing
- Restart services if needed: `anon-web stop && anon-web start`

**SSL/Certificate errors during installation?**
- Try installing with trusted hosts: `pip install --trusted-host github.com --trusted-host objects.githubusercontent.com simple-anonymizer`
- For spaCy models: `pip install --trusted-host github.com --trusted-host objects.githubusercontent.com https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl`
- Or run the model setup utility: `anon-setup-models`
- The anonymizer will still work with always-redact and pattern matching even without advanced NER models

**Models not downloading?**
- Check your internet connection and firewall settings
- Try manual installation using the URLs provided in the Model Setup section
- Use `anon-setup-models` for automatic retry with SSL workarounds
- Verify models are installed: `python -c "import spacy; print(spacy.util.get_installed_models())"`

---

**Need help?** Check the logs in `~/.anonymizer/` for detailed error information.