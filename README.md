# Intelligent Code Analyzer

🧠 A sophisticated code analysis system that combines static analysis tools with Large Language Model intelligence to provide comprehensive code review, quality assessment, and **automated fix generation with pull request workflow**.

## ✨ Features

- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust
- **Static Analysis Integration**: Flake8, Pylint, ESLint, and more
- **LLM-Powered Analysis**: Uses AWS Bedrock Claude for intelligent code review
- **Iterative Improvement**: Feedback loop with progressive code enhancement
- **🆕 Automated Fix Generation**: AI-powered code fixes with testing and PR creation
- **Comprehensive Reporting**: Detailed analysis reports and progress tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS credentials configured (for Bedrock)
- Git and GitHub CLI (`gh`) for auto-fix PR workflow
- Optional: Static analysis tools (flake8, pylint, etc.)

### Installation
```bash
# Clone the repository
git clone https://github.com/ricardosalcedo/intelligent-code-analyzer.git
cd intelligent-code-analyzer

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Install GitHub CLI (for auto-fix PRs)
# macOS: brew install gh
# Login: gh auth login
```

### Basic Usage
```bash
# Analyze a single file
python3 code_review_cli.py myfile.py

# Analyze with iterative improvement
python3 code_review_cli.py myfile.py --iterative --iterations 3

# 🆕 Auto-fix with pull request (NEW!)
python3 auto_fix_cli.py myfile.py

# Preview fixes without applying (dry-run)
python3 auto_fix_cli.py myfile.py --dry-run

# Analyze entire directory
python3 code_review_cli.py src/ --recursive
```

## 🤖 Automated Fix Workflow (NEW!)

The auto-fix system provides a complete workflow from analysis to pull request:

### How It Works
1. **📊 Analysis**: Identifies code issues using static analysis + LLM
2. **🛠️ Fix Generation**: Creates specific code fixes using AI
3. **🧪 Testing**: Validates fixes (syntax, static analysis, imports)
4. **🌿 Branch Creation**: Creates feature branch automatically
5. **📝 Pull Request**: Creates PR with detailed description
6. **👥 Review & Merge**: Team reviews and approves changes

### Auto-Fix Example
```bash
# Run auto-fix on a file with issues
python3 auto_fix_cli.py problematic_code.py

# Output:
🤖 Automated Code Fix Workflow
========================================
🔧 Starting auto-fix workflow for problematic_code.py
📊 Step 1: Analyzing code...
   Found 4 issues, quality score: 3/10
🛠️  Step 2: Generating fixes...
   Generated 3 fixes
🔨 Step 3: Applying fixes...
🧪 Step 4: Testing fixes...
✅ All tests passed
🌿 Step 5: Creating pull request...
✅ Pull request created: https://github.com/user/repo/pull/1
```

## 📊 Example Output

### Code Analysis
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
   🔴 HIGH: 1 (Security: eval() with user input)
   🟡 MEDIUM: 2 (Resource leaks, division by zero)
   🟢 LOW: 1 (Style issues)

💡 Top Recommendations:
   1. Replace eval() with ast.literal_eval() for security
   2. Use context managers for file operations
   3. Add input validation and error handling
```

### Auto-Fix Results
```
📊 Workflow Summary:
   File: example.py
   Success: ✅
   Pull Request: https://github.com/user/repo/pull/1

📋 Steps:
   ✅ Analysis: completed (4 issues found, quality: 3/10)
   ✅ Fix Generation: completed (3 fixes generated)
   ✅ Apply Fixes: completed
   ✅ Testing: passed (syntax ✅, imports ✅)
   ✅ Create PR: completed
```

## 🔧 Components

- **`code_analyzer.py`** - Core analysis engine with multi-language support
- **`smart_code_analyzer.py`** - Enhanced analyzer with feedback loop capabilities
- **`code_review_cli.py`** - Production-ready command-line interface
- **`auto_fix_pr.py`** - 🆕 Automated fix generation and PR workflow
- **`auto_fix_cli.py`** - 🆕 CLI for auto-fix operations
- **`enhanced_code_analyzer.py`** - Advanced iterative improvement features

## 📈 Analysis Types

- **Security Analysis**: Identifies vulnerabilities and security anti-patterns
- **Performance Review**: Spots performance bottlenecks and inefficiencies
- **Code Quality**: Evaluates maintainability, readability, and best practices
- **Bug Detection**: Finds potential runtime errors and logic issues
- **Style Compliance**: Checks adherence to coding standards

## 🎯 Use Cases

### Individual Developer Workflow
```bash
# Daily code quality check
python3 code_review_cli.py myfile.py

# Auto-fix common issues
python3 auto_fix_cli.py myfile.py
```

### Team Code Review Process
```bash
# Automated pre-review analysis
python3 code_review_cli.py src/ --recursive --report review.md

# Auto-fix with team approval
python3 auto_fix_cli.py src/main.py  # Creates PR for team review
```

### CI/CD Integration
```bash
# Quality gate in pipeline
python3 code_review_cli.py . --recursive --output quality_report.json

# Automated fix suggestions
python3 auto_fix_cli.py changed_files.py --dry-run
```

## 🆕 Auto-Fix Capabilities

### Supported Fix Types
- **Security Issues**: Replace `eval()` with `ast.literal_eval()`, fix SQL injection patterns
- **Resource Management**: Add context managers for file operations
- **Error Handling**: Add try/except blocks for potential failures
- **Style Issues**: Fix PEP 8 violations, improve naming conventions
- **Performance**: Optimize loops, remove redundant operations
- **Bug Prevention**: Add null checks, fix division by zero

### Safety Features
- **Syntax Validation**: Ensures fixed code compiles correctly
- **Import Testing**: Verifies modules can be imported
- **Static Analysis**: Runs quality checks on fixed code
- **Human Review**: All fixes go through pull request approval
- **Rollback Capability**: Easy to revert if issues arise

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
- GitHub for excellent CLI and API
- Open source community

---

**Ready to improve your code quality with AI-powered automation?** 🚀

Try the auto-fix workflow: `python3 auto_fix_cli.py your_file.py`
