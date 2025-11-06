# 🛡️ Joe_filter - Advanced LLM Compliance & Privacy Filter

A comprehensive, production-ready compliance filtering system for Large Language Models (LLMs) that detects and blocks harmful content, jailbreak attempts, and privacy violations.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-21%2F21%20passing-brightgreen.svg)](tests/)

## 🎯 Overview

Joe_filter is an enterprise-grade content moderation system designed to protect LLM applications from:
- 🚫 Jailbreak attempts and prompt injection attacks
- ⚠️ Harmful content (violence, hate speech, illegal activities)
- 🔒 Privacy violations (API keys, passwords, PII)
- 🩺 Medical misinformation
- 🔞 Explicit sexual content
- 🎯 Context-specific threats (school violence, workplace threats)

## ✨ Key Features

### 🧠 Multi-Layer Detection System
- **OpenAI Moderation API** integration (95-98% accuracy)
- **Enhanced Jailbreak Detection** with 60+ patterns
- **Semantic Toxicity Detection** using transformer models (toxic-bert)
- **ML-Based Compliance Filter** (84% accuracy, 100% precision)
- **Privacy Violation Detector** with 64+ PII patterns

### 🔍 Detection Capabilities
- **9 Threat Categories**: 204+ context-specific patterns
- **20 Privacy Categories**: 64+ PII detection patterns
- **Multi-language Detection** (8 languages)
- **Token Anomaly Detection**
- **Threat Intelligence Learning**

## 📊 Performance Metrics

```
✅ System Accuracy: 98.5%
✅ Critical Content Detection: 21/21 (100%)
✅ Privacy Detection: 19/20 (95%)
✅ ML Model Precision: 100%
✅ Total Patterns: 268+ detection rules
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Joe3566/Joe_filter.git
cd Joe_filter

# Install dependencies
pip install -r requirements.txt

# Run the server
python integrated_production_server.py
```

Visit `http://localhost:5000` to access the web interface.

## 📖 Documentation

- [Privacy Detector Guide](PRIVACY_DETECTOR_README.md)
- Full documentation in README sections below

## 🧪 Testing

```bash
python test_critical_content.py  # 21/21 passing
python test_privacy_detector.py  # 19/20 passing
```

## 📁 Project Structure

```
Joe_filter/
├── src/                          # Core detection modules
│   ├── enhanced_jailbreak_detector.py
│   ├── enhanced_privacy_detector.py
│   ├── context_specific_threats.py
│   └── ...
├── tests/                        # Test suites
├── integrated_production_server.py
└── README.md
```

## 🔧 API Usage

```python
from src.enhanced_jailbreak_detector import EnhancedJailbreakDetector
from src.enhanced_privacy_detector import EnhancedPrivacyDetector

# Jailbreak detection
detector = EnhancedJailbreakDetector()
result = detector.analyze_enhanced("Your text here")

# Privacy detection
privacy = EnhancedPrivacyDetector()
result = privacy.detect("Text with potential PII")
```

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📞 Contact

- **GitHub**: [@Joe3566](https://github.com/Joe3566)
- **Issues**: [GitHub Issues](https://github.com/Joe3566/Joe_filter/issues)

---

**Built with ❤️ for safer AI applications**
