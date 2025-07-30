import pytest
import os
import tempfile
import shutil
import json
from typer.testing import CliRunner
from promptvc.cli import app
from promptvc.repo import PromptRepo
from promptvc import cli

class TestCLI:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        self.runner = CliRunner()
    
    def teardown_method(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_init_command(self):
        result = self.runner.invoke(app, ["init"])
        
        assert result.exit_code == 0
        assert "Created promptvc.yaml" in result.output
        assert "Initialized prompt repo" in result.output
        assert os.path.exists(".promptvc")
        assert os.path.exists("promptvc.yaml")
    
    def test_init_existing_config(self):
        f = open("promptvc.yaml", "w")
        f.write("test")
        f.close()
        
        result = self.runner.invoke(app, ["init"])
        
        assert result.exit_code == 0
        assert "Config file already exists" in result.output
    
    def test_add_command(self):
        self.runner.invoke(app, ["init"])
        result = self.runner.invoke(app, ["add", "test-prompt", "Hello {input}"])
        
        assert result.exit_code == 0
        assert "Added/updated prompt 'test-prompt' (staged)" in result.output
        
        repo = PromptRepo()
        versions = repo._load_versions("test-prompt")
        assert len(versions) == 1
        assert versions[0]["text"] == "Hello {input}"
    
    def test_commit_command(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello world"])
        result = self.runner.invoke(app, ["commit", "test-prompt", "Initial version"])
        
        assert result.exit_code == 0
        assert "Committed prompt 'test-prompt' with message: Initial version" in result.output
        
        repo = PromptRepo()
        versions = repo._load_versions("test-prompt")
        assert versions[0]["commit_msg"] == "Initial version"
    
    def test_history_command(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Version 1"])
        self.runner.invoke(app, ["commit", "test-prompt", "First"])
        self.runner.invoke(app, ["add", "test-prompt", "Version 2"])
        self.runner.invoke(app, ["commit", "test-prompt", "Second"])
        
        result = self.runner.invoke(app, ["history", "test-prompt"])
        
        assert result.exit_code == 0
        assert "Version 1: First" in result.output
        assert "Version 2: Second" in result.output
    
    def test_checkout_command(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello world"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        
        result = self.runner.invoke(app, ["checkout", "test-prompt", "1"])
        
        assert result.exit_code == 0
        assert "Hello world" in result.output
    
    def test_checkout_invalid_version(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello world"])
        
        result = self.runner.invoke(app, ["checkout", "test-prompt", "999"])
        
        assert result.exit_code == 0
        assert "Version not found" in result.output
    
    def test_diff_command(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello world"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello universe"])
        self.runner.invoke(app, ["commit", "test-prompt", "v2"])
        
        result = self.runner.invoke(app, ["diff", "test-prompt", "1", "2"])
        
        assert result.exit_code == 0
        assert "Text Diff:" in result.output
        assert "Semantic Similarity:" in result.output
    
    def test_list_command(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "prompt1", "Test 1"])
        self.runner.invoke(app, ["add", "prompt2", "Test 2"])
        
        result = self.runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "prompt1" in result.output
        assert "prompt2" in result.output
    
    def test_init_samples_command(self):
        self.runner.invoke(app, ["init"])
        result = self.runner.invoke(app, ["init-samples", "test-prompt"])
        
        assert result.exit_code == 0
        assert "Created test-prompt_samples.json" in result.output
        assert "Edit the file with your test inputs" in result.output
        
        assert os.path.exists("test-prompt_samples.json")
        
        f = open("test-prompt_samples.json", "r")
        samples = json.load(f)
        f.close()
        
        assert len(samples) == 3
        assert "Replace with your first test input" in samples[0]["input"]
    
    def test_init_samples_existing_file(self):
        self.runner.invoke(app, ["init"])
        
        f = open("test-prompt_samples.json", "w")
        json.dump([{"input": "existing"}], f)
        f.close()
        
        result = self.runner.invoke(app, ["init-samples", "test-prompt"])
        
        assert result.exit_code == 0
        assert "already exists" in result.output
    
    def test_no_samples(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello {input}"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        
        result = self.runner.invoke(app, ["test", "test-prompt", "1", "1"])
        
        assert result.exit_code == 0
        assert "Samples file 'test-prompt_samples.json' not found" in result.output
        assert "Creating template..." in result.output
        assert "Edit the file with your test inputs and rerun" in result.output
        
        assert os.path.exists("test-prompt_samples.json")
    
    def test_invalid_llm(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello {input}"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        
        samples = [{"input": "test"}]
        f = open("test-prompt_samples.json", "w")
        json.dump(samples, f)
        f.close()
        
        result = self.runner.invoke(app, ["test", "test-prompt", "1", "1", "--llm", "invalid"])
        
        assert result.exit_code == 0
        assert "Invalid LLM" in result.output
        assert "openai" in result.output
        assert "anthropic" in result.output
    
    def test_success(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Summarize: {input}"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        self.runner.invoke(app, ["add", "test-prompt", "Provide summary: {input}"])
        self.runner.invoke(app, ["commit", "test-prompt", "v2"])
        
        samples = [{"input": "test article"}]
        f = open("test-prompt_samples.json", "w")
        json.dump(samples, f)
        f.close()
        
        original_openai = cli.LLM_CALLERS["openai"]
        original_anthropic = cli.LLM_CALLERS["anthropic"]
        
        def mock_llm(prompt):
            return f"Mock response to: {prompt}"
        
        cli.LLM_CALLERS["openai"] = mock_llm
        cli.LLM_CALLERS["anthropic"] = mock_llm
        
        result = self.runner.invoke(app, ["test", "test-prompt", "1", "2"])
        
        cli.LLM_CALLERS["openai"] = original_openai
        cli.LLM_CALLERS["anthropic"] = original_anthropic
        
        assert result.exit_code == 0
        assert "Testing test-prompt versions 1 vs 2" in result.output
        assert "Comparison Results:" in result.output
        assert "Test 1:" in result.output
        assert "Mock response to:" in result.output
        assert "Similarity:" in result.output
    
    def test_version_not_found(self):
        self.runner.invoke(app, ["init"])
        self.runner.invoke(app, ["add", "test-prompt", "Hello {input}"])
        self.runner.invoke(app, ["commit", "test-prompt", "v1"])
        
        samples = [{"input": "test"}]
        f = open("test-prompt_samples.json", "w")
        json.dump(samples, f)
        f.close()
        
        result = self.runner.invoke(app, ["test", "test-prompt", "1", "999"])
        
        assert result.exit_code == 0
        assert "One or both versions not found" in result.output


class TestCLIWorkflow:
    
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        self.runner = CliRunner()
    
    def teardown_method(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_complete_workflow(self):
        result = self.runner.invoke(app, ["init"])
        assert result.exit_code == 0
        
        result = self.runner.invoke(app, ["add", "summarizer", "Summarize this: {input}"])
        assert result.exit_code == 0
        
        result = self.runner.invoke(app, ["commit", "summarizer", "v1"])
        assert result.exit_code == 0
        
        result = self.runner.invoke(app, ["add", "summarizer", "Provide summary: {input}"])
        assert result.exit_code == 0
        
        result = self.runner.invoke(app, ["commit", "summarizer", "v2"])
        assert result.exit_code == 0
        
        result = self.runner.invoke(app, ["history", "summarizer"])
        assert result.exit_code == 0
        assert "Version 1: v1" in result.output
        assert "Version 2: v2" in result.output
        
        result = self.runner.invoke(app, ["init-samples", "summarizer"])
        assert result.exit_code == 0
        
        samples = [{"input": "This is a test article about AI"}]
        f = open("summarizer_samples.json", "w")
        json.dump(samples, f)
        f.close()
        
        result = self.runner.invoke(app, ["test", "summarizer", "1", "2"])
        assert result.exit_code == 0
        assert "Testing summarizer versions 1 vs 2" in result.output

if __name__ == "__main__":
    pytest.main([__file__])