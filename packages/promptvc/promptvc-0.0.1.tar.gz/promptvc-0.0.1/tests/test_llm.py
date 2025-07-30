import pytest
import os
import tempfile
import shutil
from promptvc.llm import call_openai, call_anthropic

class TestLLMFunctions:
    def setup(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)

    def test_call_openai_no_config_file(self):
        result = call_openai("Test prompt")
        
        assert "Error calling OpenAI:" in result
        assert "Config file not found" in result

    def test_call_openai_no_provider(self):
        config_content = """\
llm_providers:
  anthropic:
    api_key: "test_key"
    default_model: "claude-3-opus"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_openai("Test prompt")
        
        assert result == "Error: OpenAI configuration not found in promptvc.yaml"

    def test_invalid_api_key(self):
        config_content = """\
llm_providers:
  openai:
    api_key: "invalid_key"
    default_model: "gpt-4-turbo"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_openai("Test prompt")
        
        assert "Error calling OpenAI:" in result

    def test_call_anthropic_no_config_file(self):
        result = call_anthropic("Test prompt")
        
        assert "Error calling Anthropic:" in result
        assert "Config file not found" in result

    def test_call_anthropic_no_provider_config(self):
        config_content = """\
llm_providers:
  openai:
    api_key: "test_key"
    default_model: "gpt-4-turbo"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_anthropic("Test prompt")
        
        assert result == "Error: Anthropic configuration not found in promptvc.yaml"

    def test_call_anthropic_invalid_api_key(self):
        config_content = """\
llm_providers:
  anthropic:
    api_key: "invalid_key"
    default_model: "claude-3-opus-20240229"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_anthropic("Test prompt")
        
        assert "Error calling Anthropic:" in result

    def test_load_diff_models(self):
        config_content = """\
llm_providers:
  openai:
    api_key: "test_key_1"
    default_model: "gpt-4-mini"
  anthropic:
    api_key: "test_key_2"
    default_model: "claude-3-sonnet-20240229"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        openai_result = call_openai("Test")
        anthropic_result = call_anthropic("Test")
        
        assert "Error calling OpenAI:" in openai_result
        assert "Error calling Anthropic:" in anthropic_result

    def test_empty_config(self):
        with open("promptvc.yaml", "w") as f:
            f.write("")
        
        openai_result = call_openai("Test")
        anthropic_result = call_anthropic("Test")
        
        assert "Error calling OpenAI:" in openai_result
        assert "Error calling Anthropic:" in anthropic_result

    def test_malformed_yaml(self):
        with open("promptvc.yaml", "w") as f:
            f.write("invalid: yaml: content: [")
        
        openai_result = call_openai("Test")
        anthropic_result = call_anthropic("Test")
        
        assert "Error calling OpenAI:" in openai_result
        assert "Error calling Anthropic:" in anthropic_result

    def test_missing_api_key(self):
        config_content = """\
llm_providers:
  openai:
    default_model: "gpt-4-turbo"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_openai("Test")
        
        assert "Error calling OpenAI:" in result

    def test_config_missing_model(self):
        config_content = """\
llm_providers:
  openai:
    api_key: "test_key"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        result = call_openai("Test")
        
        assert "Error calling OpenAI:" in result

if __name__ == "__main__":
    pytest.main([__file__])