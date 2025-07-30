import typer
from promptvc.repo import PromptRepo
import os
import json

from .llm import call_openai, call_anthropic

LLM_CALLERS = {
    "openai": call_openai,
    "anthropic": call_anthropic,
}

app = typer.Typer(help="Git-like version control for LLM prompts.")

@app.command()
def init(path="."):
    repo = PromptRepo(path)
    config_path = os.path.join(path, "promptvc.yaml")
    gitignore_path = os.path.join(path, ".gitignore")

    if not os.path.exists(config_path):
        template_config = """\
llm_providers:
  openai:
    api_key: "your_openai_api_key"
    default_model: "gpt-4-turbo"
  anthropic:
    api_key: "your_anthropic_api_key"
    default_model: "claude-3-opus-20240229"
"""
        with open(config_path, "w") as f:
            f.write(template_config)
        typer.echo("Created promptvc.yaml")
    else:
        typer.echo("Config file already exists")

    try:
        with open(gitignore_path, "a+") as f:
            f.seek(0)
            lines = f.readlines()
            found = False
            for line in lines:
                if "promptvc.yaml" in line:
                    found = True
                    break
            if not found:
                f.write("\n# promptvc config\npromptvc.yaml\n")
                typer.echo("Added promptvc.yaml to .gitignore")
    except IOError:
        pass

    typer.echo(f"Initialized prompt repo at {repo.repo_path}")

@app.command()
def add(name, text):
    repo = PromptRepo()
    repo.add(name, text)
    typer.echo(f"Added/updated prompt '{name}' (staged)")

@app.command()
def commit(name, msg):
    repo = PromptRepo(".")
    repo.commit(name, msg)
    typer.echo(f"Committed prompt '{name}' with message: {msg}")

@app.command()
def history(name):
    repo = PromptRepo(".")
    versions = repo.history(name)
    for v in versions:
        typer.echo(f"Version {v.id}: {v.commit_msg} ({v.timestamp})")

@app.command()
def checkout(name, version):
    repo = PromptRepo(".")
    text = repo.checkout(name, int(version))
    if text:
        typer.echo(text)
    else:
        typer.echo("Version not found")

@app.command()
def diff(name, v1, v2):
    repo = PromptRepo(".")
    result = repo.diff(name, int(v1), int(v2))
    typer.echo("Text Diff:\n" + result["text_diff"])
    typer.echo(f"\nSemantic Similarity: {result['semantic_similarity']:.2f}")

@app.command(name="list")
def list_prompts():
    repo = PromptRepo(".")
    files = os.listdir(repo.prompts_dir)
    for f in files:
        if f.endswith('.yaml') and '_baseline' not in f:
            typer.echo(f.replace('.yaml', ''))

@app.command() 
def init_samples(name):
    samples_file = f"{name}_samples.json"
    
    if os.path.exists(samples_file):
        typer.echo(f"Samples file '{samples_file}' already exists")
        return
    
    template_samples = [
        {"input": "Replace with your first test input"},
        {"input": "Replace with your second test input"},
        {"input": "Add more test cases if you need"}
    ]
    
    with open(samples_file, "w") as f:
        json.dump(template_samples, f, indent=2)
    
    typer.echo(f"Created {samples_file}")
    typer.echo("Edit the file with your test inputs")

@app.command()
def test(name, v1, v2, llm="openai"):
    repo = PromptRepo(".")
    samples_file = f"{name}_samples.json"
    
    if not os.path.exists(samples_file):
        typer.echo(f"Samples file '{samples_file}' not found")
        typer.echo(f"Creating template...")
        
        template_samples = [
            {"input": "Replace with your first test input"},
            {"input": "Replace with your second test input"}
        ]
        
        with open(samples_file, "w") as f:
            json.dump(template_samples, f, indent=2)
        
        typer.echo(f"Created {samples_file}")
        typer.echo("Edit the file with your test inputs and rerun")
        return
    
    if llm not in LLM_CALLERS:
        available = []
        for key in LLM_CALLERS.keys():
            available.append(key)
        typer.echo(f"Invalid LLM. Choose from: {available}")
        return
    
    with open(samples_file, 'r') as f:
        samples = json.load(f)
    
    typer.echo(f"Testing {name} versions {v1} vs {v2} using {llm}...")
    
    v1_int = int(v1)
    v2_int = int(v2)
    
    results = repo.eval_versions(name, [v1_int, v2_int], samples, LLM_CALLERS[llm])

    if v1_int not in results or v2_int not in results:
        typer.echo("One or both versions not found")
        return
    
    v1_outputs = results[v1_int]["outputs"] 
    v2_outputs = results[v2_int]["outputs"]
    
    typer.echo(f"\nComparison Results:")
    typer.echo("=" * 50)
    
    for i, (out1, out2) in enumerate(zip(v1_outputs, v2_outputs)):
        typer.echo(f"\nTest {i+1}:")
        typer.echo(f"Input: {out1['input']}")
        typer.echo(f"V{v1}: {out1['output']}")
        typer.echo(f"V{v2}: {out2['output']}")
        
        similarity = repo.diff_engine.semantic_diff(out1['output'], out2['output'])
        typer.echo(f"Similarity: {similarity:.2f}")
        typer.echo("-" * 30)

if __name__ == "__main__":
    app()