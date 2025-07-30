import os
import hashlib
import anthropic
from pathlib import Path
import typer

app = typer.Typer(no_args_is_help=True)

HASH_FILE_NAME = ".tf_readme_hash"

def read_terraform_files(project_path):
    tf_code = ""
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".tf"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():  # Only include non-empty files
                        tf_code += f"\n# File: {file_path}\n" + content + "\n"
    return tf_code

def compute_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_previous_hash(project_path):
    hash_path = os.path.join(project_path, HASH_FILE_NAME)
    if os.path.exists(hash_path):
        with open(hash_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_current_hash(project_path, hash_value):
    hash_path = os.path.join(project_path, HASH_FILE_NAME)
    with open(hash_path, "w", encoding="utf-8") as f:
        f.write(hash_value)

def call_claude_for_readme(tf_code, client):
    system_prompt = "You are an expert DevOps engineer who writes clean, helpful documentation."

    user_prompt = f'''
You are reviewing a Terraform project. Based on the following Terraform configuration files, generate a comprehensive README.md that explains the infrastructure in clear sections, such as:

- Project Overview
- Infrastructure Components
- Networking
- Security
- IAM Roles & Permissions
- Storage
- Compute Resources
- Observability
- Cost Considerations
- How to Deploy
- How to Destroy
- Prerequisites
- Terraform Version

Make sure the README is production-ready and easy for new developers to understand. And make sure to highlight the important details in BOLD.
Also make sure to include a section for expected cost range and another sections for possible improvements.

Dont add any license or contribution related sections.
Just start your output with the doc right away.
Terraform Code:
~~~
{tf_code}
~~~
'''
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1500,
        temperature=0.5,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text

def call_claude_for_inline_comments(file_content, client):
    system_prompt = "You are a Terraform expert who adds helpful inline comments to Terraform code."

    user_prompt = f'''
Add **clear inline comments** to the following Terraform file to help a junior DevOps engineer understand what each block or line is doing. Be concise but informative.

Respond only with the updated code. Do not wrap the code with markdown backticks (e.g. ```hcl). Just return plain HCL with comments added.

Terraform Code:
~~~
{file_content}
~~~
'''
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1500,
        temperature=0.3,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```") and raw.endswith("```"):
        lines = raw.splitlines()
        return "\n".join(lines[1:-1])
    return raw

def add_inline_comments_to_tf_files(project_path, client):
    typer.echo("[*] Adding inline comments to .tf files...")
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".tf"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    original_content = f.read()
                if not original_content.strip():
                    typer.echo(f"[!] Skipping empty file: {file_path}")
                    continue
                updated_content = call_claude_for_inline_comments(original_content, client)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                typer.echo(f"[✓] Comments added to: {file_path}")

@app.command()
def review(path: str = typer.Argument(..., help="Path to the Terraform project directory")):
    """Generate README.md and inline comments for a Terraform project."""
    tf_project_path = Path(path)
    if not tf_project_path.exists():
        typer.echo(f"❌ Path '{tf_project_path}' does not exist.")
        raise typer.Exit(code=1)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        typer.echo("❌ ANTHROPIC_API_KEY environment variable not set.")
        raise typer.Exit(code=1)

    typer.echo("[*] Reading Terraform files...")
    tf_code = read_terraform_files(tf_project_path)

    if not tf_code.strip():
        typer.echo("❌ No .tf files found or files are empty.")
        raise typer.Exit(code=1)

    current_hash = compute_hash(tf_code)
    previous_hash = load_previous_hash(tf_project_path)

    if current_hash == previous_hash:
        typer.echo("✅ No changes detected since last generation. Skipping...")
        raise typer.Exit()

    typer.echo("[*] Sending updated code to Claude...")
    client = anthropic.Anthropic(api_key=api_key)

    readme_text = call_claude_for_readme(tf_code, client)
    readme_path = tf_project_path / "README.md"
    readme_path.write_text(readme_text, encoding="utf-8")
    typer.echo(f"✅ README.md created: {readme_path}")

    add_inline_comments_to_tf_files(tf_project_path, client)

    save_current_hash(tf_project_path, current_hash)
    typer.echo("✅ Done. Terraform files are now commented.")

if __name__ == "__main__":
    app()
