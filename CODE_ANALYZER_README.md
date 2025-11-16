# Intelligent Code Analyzer with LLM Feedback Loop

A sophisticated code analysis system that combines static analysis tools with Large Language Model (LLM) intelligence to provide comprehensive code review, quality assessment, and iterative improvement suggestions.

## 🎯 Features

### Core Capabilities
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C/C++
- **Static Analysis Integration**: Flake8, Pylint, ESLint, and more
- **LLM-Powered Analysis**: Uses AWS Bedrock Claude for intelligent code review
- **Iterative Improvement**: Feedback loop with progressive code enhancement
- **Comprehensive Reporting**: Detailed analysis reports and progress tracking

### Analysis Types
1. **Security Analysis**: Identifies vulnerabilities and security anti-patterns
2. **Performance Review**: Spots performance bottlenecks and inefficiencies  
3. **Code Quality**: Evaluates maintainability, readability, and best practices
4. **Bug Detection**: Finds potential runtime errors and logic issues
5. **Style Compliance**: Checks adherence to coding standards

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS credentials configured (for Bedrock)
- Optional: Static analysis tools (flake8, pylint, etc.)

### Installation
```bash
# Install Python dependencies
pip install boto3

# Optional: Install static analysis tools
pip install flake8 pylint bandit

# For JavaScript/TypeScript
npm install -g eslint tslint

# For Go
go install golang.org/x/lint/golint@latest
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

## 📁 Project Structure

```
code-analyzer/
├── code_analyzer.py           # Core analysis engine
├── smart_code_analyzer.py     # Enhanced analyzer with feedback loop
├── enhanced_code_analyzer.py  # Advanced iterative improvement
├── code_review_cli.py         # Command-line interface
├── analyze_code.py            # Simple CLI wrapper
└── CODE_ANALYZER_README.md    # This documentation
```

## 🔧 Components

### 1. Static Analysis Engine (`StaticAnalyzer`)
Runs language-specific static analysis tools:

```python
analyzer = StaticAnalyzer()
result = analyzer.analyze_file("mycode.py")
```

**Supported Tools by Language:**
- **Python**: flake8, pylint, bandit, mypy
- **JavaScript**: ESLint
- **TypeScript**: TSLint, ESLint
- **Java**: javac, SpotBugs, PMD
- **Go**: go vet, golint
- **Rust**: clippy

### 2. LLM Analysis Engine (`LLMAnalyzer`)
Uses AWS Bedrock Claude for intelligent analysis:

```python
llm_analyzer = LLMAnalyzer()
insights = llm_analyzer.analyze_results(static_results, code_content)
```

**LLM Analysis Provides:**
- Quality scoring (1-10)
- Issue categorization (security, performance, style, bugs)
- Specific recommendations
- Code improvement suggestions
- Security vulnerability assessment

### 3. Feedback Loop System (`FeedbackLoop`)
Manages iterative improvement cycles:

```python
feedback = FeedbackLoop()
suggestions = feedback.generate_improvement_suggestions(analysis, code)
improved_code = feedback.apply_suggestions(original_code, suggestions)
```

### 4. Smart Code Analyzer (`SmartCodeAnalyzer`)
Integrated system combining all components:

```python
analyzer = SmartCodeAnalyzer()
results = analyzer.iterative_improvement("myfile.py", iterations=3)
```

## 📊 Analysis Output

### Single File Analysis
```json
{
  "file_path": "example.py",
  "language": "python",
  "lines_of_code": 45,
  "static_analysis": {
    "tools_used": ["flake8"],
    "issues": [...],
    "syntax_valid": true
  },
  "llm_analysis": {
    "quality_score": 7,
    "issues": [
      {
        "type": "security",
        "severity": "high", 
        "description": "Use of eval() with user input",
        "line": 23
      }
    ],
    "recommendations": [
      "Replace eval() with ast.literal_eval() for safer evaluation",
      "Add input validation and sanitization"
    ],
    "overall_assessment": "Good structure but security concerns need attention"
  }
}
```

### Iterative Analysis Results
```json
{
  "file_path": "example.py",
  "iterations": [
    {
      "iteration": 1,
      "quality_score": 5,
      "issues_count": 8
    },
    {
      "iteration": 2, 
      "quality_score": 7,
      "issues_count": 4
    }
  ],
  "progress_summary": {
    "quality_improvement": 2.0,
    "issues_resolved": 4,
    "final_quality": 7
  }
}
```

## 🎮 Usage Examples

### Example 1: Basic File Analysis
```bash
python3 code_review_cli.py app.py
```
Output:
```
🧠 Intelligent Code Review Tool
========================================

📁 app.py
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

### Example 2: Iterative Improvement
```bash
python3 code_review_cli.py buggy_code.py --iterative --iterations 3 --report improvement_report.md
```
Output:
```
🔄 Iterative Analysis Results
📁 File: buggy_code.py

📈 Progress Summary:
   Initial Quality: 4/10
   Final Quality: 8/10
   Improvement: +4.0 points
   Issues Resolved: 6

📊 Quality Trend:
   4/10 → 6/10 → 8/10
```

### Example 3: Directory Analysis
```bash
python3 code_review_cli.py src/ --recursive --output full_analysis.json
```
Output:
```
📂 Analyzing directory: src/
📋 Found 12 files to analyze

🔍 Analyzing: main.py
   Quality: 8/10, Issues: 2
🔍 Analyzing: utils.py  
   Quality: 6/10, Issues: 5
🔍 Analyzing: config.py
   Quality: 9/10, Issues: 1

📊 Summary Statistics:
   Files analyzed: 12
   Average quality: 7.2/10
   Total issues: 28
   Average issues per file: 2.3
```

## 🔍 Analysis Categories

### Security Issues
- Code injection vulnerabilities (eval, exec)
- Unsafe deserialization (pickle)
- Path traversal vulnerabilities
- SQL injection patterns
- Hardcoded credentials

### Performance Issues  
- Inefficient algorithms (O(n²) when O(n) possible)
- Memory leaks
- Unnecessary computations in loops
- Blocking I/O operations
- Large object creation in loops

### Code Quality Issues
- Unused variables and functions
- Complex functions (high cyclomatic complexity)
- Poor naming conventions
- Missing documentation
- Inconsistent formatting

### Bug Patterns
- Division by zero potential
- Null pointer dereferences
- Array bounds violations
- Resource leaks (unclosed files)
- Race conditions

## 🎯 Integration Examples

### With CI/CD Pipeline
```yaml
# .github/workflows/code-analysis.yml
name: Code Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install boto3 flake8 pylint
      - name: Run code analysis
        run: python3 code_review_cli.py src/ --recursive --output analysis.json
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### With Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit
python3 code_review_cli.py $(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts)$')
```

### Programmatic Usage
```python
from smart_code_analyzer import SmartCodeAnalyzer

analyzer = SmartCodeAnalyzer()

# Analyze single file
result = analyzer.analyze_file("mycode.py")
quality_score = result['llm_analysis']['quality_score']

if quality_score < 6:
    print("Code quality below threshold!")
    
# Iterative improvement
improvement_results = analyzer.iterative_improvement("mycode.py", iterations=2)
print(f"Quality improved by {improvement_results['progress_summary']['quality_improvement']} points")
```

## 🔧 Configuration

### AWS Bedrock Setup
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret  
export AWS_DEFAULT_REGION=us-west-2
```

### Custom Model Configuration
```python
# In smart_code_analyzer.py, modify:
self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"  # Faster, cheaper
# or
self.model_id = "anthropic.claude-3-opus-20240229-v1:0"   # More capable
```

## 📈 Performance & Costs

### Analysis Speed
- **Single file**: 5-15 seconds (depending on file size and LLM response time)
- **Directory (10 files)**: 1-3 minutes
- **Large codebase (100+ files)**: 10-30 minutes

### AWS Bedrock Costs (Approximate)
- **Claude 3 Sonnet**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Typical analysis**: 2-5K tokens input, 1-2K tokens output
- **Cost per file**: ~$0.01-0.03
- **Cost per 100 files**: ~$1-3

## 🚀 Advanced Features

### Custom Analysis Rules
```python
# Add custom analysis patterns
custom_rules = {
    'security': [
        {'pattern': r'subprocess\.call\(.*shell=True', 'severity': 'high'},
        {'pattern': r'pickle\.loads?\(', 'severity': 'medium'}
    ]
}
```

### Integration with IDEs
- VS Code extension (planned)
- Vim/Neovim plugin (planned)  
- IntelliJ plugin (planned)

### Batch Processing
```python
# Process multiple repositories
repos = ['repo1/', 'repo2/', 'repo3/']
for repo in repos:
    results = analyzer.analyze_directory(repo)
    generate_report(results, f"{repo}_analysis.md")
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AWS Bedrock team for Claude API
- Static analysis tool maintainers (flake8, pylint, ESLint, etc.)
- Open source community for inspiration and feedback

---

**Ready to improve your code quality?** Start with `python3 code_review_cli.py your_file.py` and see the magic happen! ✨
