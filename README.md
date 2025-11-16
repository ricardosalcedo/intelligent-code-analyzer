# Intelligent Code Analyzer

🧠 A sophisticated code analysis system that combines static analysis tools with Large Language Model intelligence to provide comprehensive code review, quality assessment, and iterative improvement suggestions.

## ✨ Features

- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust
- **Static Analysis Integration**: Flake8, Pylint, ESLint, and more
- **LLM-Powered Analysis**: Uses AWS Bedrock Claude for intelligent code review
- **Iterative Improvement**: Feedback loop with progressive code enhancement
- **Comprehensive Reporting**: Detailed analysis reports and progress tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS credentials configured (for Bedrock)
- Optional: Static analysis tools (flake8, pylint, etc.)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/intelligent-code-analyzer.git
cd intelligent-code-analyzer

# Install dependencies
pip install -r code_analyzer_requirements.txt

# Configure AWS credentials
aws configure
```

### Basic Usage
```bash
# Analyze a single file
python3 code_review_cli.py myfile.py

# Analyze with iterative improvement
python3 code_review_cli.py myfile.py --iterative --iterations 3

# Analyze entire directory
python3 code_review_cli.py src/ --recursive

# Generate detailed report
python3 code_review_cli.py app.py --report analysis_report.md --output results.json
```

## 📊 Example Output

```
🧠 Intelligent Code Review Tool
========================================

📁 example.py
🔤 Language: PYTHON
📏 Lines of code: 67
✅ Syntax: Valid
📊 Quality Score: 6/10
🟡 Good code quality with room for improvement

🚨 Issues Found: 4
   🔴 HIGH: 1
   🟡 MEDIUM: 2
   🟢 LOW: 1

💡 Top Recommendations:
   1. Add error handling for file operations
   2. Use context managers for resource management
   3. Validate user input before processing
```

## 🔧 Components

- **`code_analyzer.py`** - Core analysis engine with multi-language support
- **`smart_code_analyzer.py`** - Enhanced analyzer with feedback loop capabilities
- **`code_review_cli.py`** - Production-ready command-line interface
- **`enhanced_code_analyzer.py`** - Advanced iterative improvement features

## 📈 Analysis Types

- **Security Analysis**: Identifies vulnerabilities and security anti-patterns
- **Performance Review**: Spots performance bottlenecks and inefficiencies
- **Code Quality**: Evaluates maintainability, readability, and best practices
- **Bug Detection**: Finds potential runtime errors and logic issues
- **Style Compliance**: Checks adherence to coding standards

## 🎯 Use Cases

- Individual developer workflow improvement
- Automated code review processes
- CI/CD pipeline integration
- Technical debt assessment
- Team code quality standards

## 📄 Documentation

- [Complete Documentation](CODE_ANALYZER_README.md)
- [Project Summary](CODE_ANALYSIS_PROJECT_SUMMARY.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Bedrock team for Claude API
- Static analysis tool maintainers
- Open source community

---

**Ready to improve your code quality with AI?** 🚀
