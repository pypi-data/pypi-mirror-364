# Terraform Reviewer

Generate production-ready Terraform documentation and inline comments using Claude AI.

## Features
- **Automatic README.md generation** for your Terraform projects
- **Inline comments** added to all `.tf` files for better understanding
- Uses [Anthropic Claude](https://www.anthropic.com/) for high-quality AI-generated documentation

## Requirements
- Python 3.8+
- [Anthropic API key](https://docs.anthropic.com/claude/docs/quickstart-guide)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Zayan-ahmed953/Terraform_Reviewer_AI_Tool.git
   cd Terraform_AI_Reviewer
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Setup

Export your Anthropic API key as an environment variable:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

From your terminal, run:
```bash
terraformreviewer /path/to/your/terraform/project
```

- This will:
  - Generate a `README.md` in your project directory, describing your infrastructure.
  - Add helpful inline comments to all `.tf` files in the project.

### Example
```bash
terraformreviewer /home/zayan/Desktop/My-Projects/AI-Generated-sample-terraform/
```

## Notes
- If you run the tool again without changing your Terraform files, it will skip regeneration for efficiency.
- Make sure your API key is valid and you have internet access.

## Troubleshooting
- **No .tf files found:** Ensure you provide the path to a directory containing Terraform files.
- **API key error:** Double-check that `ANTHROPIC_API_KEY` is set in your environment.
- **Other errors:** Please open an issue with the error message and steps to reproduce.

## License
MIT 