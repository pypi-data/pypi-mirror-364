import pytest
import tempfile
import shutil
import os
from promptvc.config import LLMProviderConfig, Config, load_config

class TestLLMProviderConfig:
    def test_init(self):
        config = LLMProviderConfig(
            api_key="test-key-123",
            default_model="gpt-4"
        )
        
        assert config.api_key == "test-key-123"
        assert config.default_model == "gpt-4"
    
class TestConfig:
    def test_init(self):
        config = Config()
        
        assert config.llm_providers == {}
        assert isinstance(config.llm_providers, dict)
    
    def test_add_provider(self):
        config = Config()
        
        openai_config = LLMProviderConfig("sk-123", "gpt-4")
        config.llm_providers["openai"] = openai_config
        
        assert "openai" in config.llm_providers
        assert config.llm_providers["openai"].api_key == "sk-123"
        assert config.llm_providers["openai"].default_model == "gpt-4"

class TestLoadConfig:
    def setup(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_config_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config()
    
    def test_config_empty_file(self):

        with open("promptvc.yaml", "w") as f:
            f.write("")
        
        with pytest.raises(ValueError, match="Empty config file"):
            load_config()
    
    def test_missing_llm_providers(self):
        config_content = """
other_section:
  some_key: some_value
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        with pytest.raises(ValueError, match="Missing llm_providers section"):
            load_config()
    
    def test_valid_single_provider(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123"
    default_model: "gpt-4"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        assert isinstance(config, Config)
        assert "openai" in config.llm_providers
        
        openai_config = config.llm_providers["openai"]
        assert isinstance(openai_config, LLMProviderConfig)
        assert openai_config.api_key == "sk-test123"
        assert openai_config.default_model == "gpt-4"
    
    def test_load_config_valid_multiple_providers(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-openai123"
    default_model: "gpt-4"
  anthropic:
    api_key: "ant-claude456"
    default_model: "claude-3-opus"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        assert len(config.llm_providers) == 2
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-openai123"
        assert openai_config.default_model == "gpt-4"
        
        anthropic_config = config.llm_providers["anthropic"]
        assert anthropic_config.api_key == "ant-claude456"
        assert anthropic_config.default_model == "claude-3-opus"
    
    def test_empty_llm_providers(self):
        config_content = """
llm_providers:
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        assert isinstance(config, Config)
        assert config.llm_providers == {}
    
    def test_missing_fields(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        with pytest.raises(KeyError):
            load_config()
    
    def test_extra_fields(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123"
    default_model: "gpt-4"
    extra_field: "should_be_ignored"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-test123"
        assert openai_config.default_model == "gpt-4"
        assert not hasattr(openai_config, "extra_field")
    
    def test_config_empty_api_key(self):
        config_content = """
llm_providers:
  openai:
    api_key: ""
    default_model: "gpt-4"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == ""
        assert openai_config.default_model == "gpt-4"
    
    def test_config_empty_model(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123"
    default_model: ""
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-test123"
        assert openai_config.default_model == ""
    
    def test_special_characters_in_values(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test!@#$%^&*()_+123"
    default_model: "gpt-4-turbo-preview"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-test!@#$%^&*()_+123"
        assert openai_config.default_model == "gpt-4-turbo-preview"
    
    def test_numeric_values(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-123456789"
    default_model: "gpt-4"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-123456789"
        assert openai_config.default_model == "gpt-4"
    
    def test_malformed_yaml(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123
    default_model: "gpt-4"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        with pytest.raises(Exception):
            load_config()
    
    def test_config_null_values(self):
        config_content = """
    llm_providers:
        openai:
            api_key: null
            default_model: "gpt-4"
    """
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key is None
        assert openai_config.default_model == "gpt-4"
    
    def test_additional_sections(self):
        config_content = """
llm_providers:
  openai:
    api_key: "sk-test123"
    default_model: "gpt-4"

other_section:
  some_key: "some_value"

random_data: 123
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        assert len(config.llm_providers) == 1
        assert "openai" in config.llm_providers
        openai_config = config.llm_providers["openai"]
        assert openai_config.api_key == "sk-test123"
    
    def test_case_sensitive_provider_names(self):
        config_content = """
llm_providers:
  OpenAI:
    api_key: "sk-test123"
    default_model: "gpt-4"
  ANTHROPIC:
    api_key: "ant-test456"
    default_model: "claude-3"
"""
        with open("promptvc.yaml", "w") as f:
            f.write(config_content)
        
        config = load_config()
        
        assert "OpenAI" in config.llm_providers
        assert "ANTHROPIC" in config.llm_providers
        assert "openai" not in config.llm_providers
        assert "anthropic" not in config.llm_providers

if __name__ == "__main__":
    pytest.main([__file__])