# PromptVC

![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![100% Local](https://img.shields.io/badge/privacy-100%25%20local-brightgreen)
![PyPI version](https://img.shields.io/pypi/v/skylos)
![Security Policy](https://img.shields.io/badge/security-policy-brightgreen)
![Dead Code Free](https://img.shields.io/badge/Dead_Code-Free-brightgreen?logo=moleculer&logoColor=white)

<div align="center">
   <img src="assets/promptvc.png" alt="promptvc Logo" width="200">
</div>

Promptvc is a lightweight and local tool for Git-like version control and A/B testing of your LLM prompts. It acts as a dev tool and version control, designed to help you find the best prompts before you add it into your workflow. Unlike an excel sheet, this is cleaner. Trust us. 

## Table of Contents
- [Why?](#why)
- [Install](#install)
- [Quick Start](#quick-start)
- [Usage](#usage)
 - [CLI Commands](#cli-commands)
 - [Python API](#python-api)
- [Full Example](#full-example)
- [Config](#config)
- [FAQ](#faq)

## Why?

Instead of guessing which prompt is better, test them:

1. Version A: "Summarize this article: {input}"
2. Version B: "Write a 2-sentence summary focusing on key insights: {input}"

See which one actually performs better with your data

## Install

```bash
pip install promptvc
```

## Quick Start
``` bash

# step 1. initialize promptvc
promptvc init

# step 2. create two prompt versions
promptvc add summarizer "Summarize this article: {input}"
promptvc commit summarizer "version A - simple"

promptvc add summarizer "Write a 2-sentence summary focusing on key insights: {input}"  
promptvc commit summarizer "version B - structured"

# step 3. create and edit your test data in the _samples.jsonn

promptvc init-samples summarizer
# inside your summarizer.json, edit your data. oh and dont forget to input your api keys

# step 4. test
promptvc test summarizer 1 2 --llm openai
```

## Usage 

#### CLI Commands 

```bash
init: Initialize new repo
add <name> <text>: Add prompt version  
commit <name> <msg>: Commit staged version
history <name>: View version history
checkout <name> <version>: Get version text
diff <name> <v1> <v2>: Compare versions
list: List all prompts
init-samples <name>: Create samples file
test <name> <v1> <v2>: Compare versions with LLM
```

### Python API

``` python
from promptvc.repo import PromptRepo
import openai

def my_llm(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# A/B test your prompts
repo = PromptRepo()
samples = [{"input": "Your test data here"}]
results = repo.eval_versions("prompt-name", [1, 2], samples, my_llm)

# compare your outputs
for version_id, result in results.items():
    print(f"Version {version_id}:")
    for output in result['outputs']:
        print(f"  {output['output']}")

```

## Full example

```bash

# test email writing prompts
promptvc add email-writer "Write a professional email about: {input}"
promptvc commit email-writer "formal version"

promptvc add email-writer "Write a friendly, concise email about: {input}"
promptvc commit email-writer "casual version"

# create your test cases

promptvc init-samples email-writer


# inside your json email-writer_samples.json:
# [
#   {"input": "quarterly sales meeting"},
#   {"input": "server maintenance window"},
#   {"input": "new product launch"}
# ]

# test
promptvc test email-writer 1 2 --llm openai
```

## Config

```yaml
llm_providers:
  openai:
    api_key: "your-key-here"
    default_model: "gpt-4o-mini"
  anthropic:
    api_key: "your-key-here"  
    default_model: "claude-3-sonnet-20240229"
```

## MISC

### Tests
For tests conducted, refer to `TEST.md`

### Tutorial
Refer to `TUTORIAL.md`

### Contribution
Refer to `CONTRIBUTING.md`

## FAQ

1. Can the library do live interactive testing?

A: The library is **not** built for live, interactive testing. The `Pipeline` class can only test a pre-scripted sequence of turns, **not** a dynamic one. The purpose of this tool is to bring version control and A/B testing to the foundational, single-turn prompts.

2. Does it work with any LLM?
A: Works with OpenAI, Anthropic for now