import os
from dataclasses import dataclass
from ruamel.yaml import YAML

@dataclass
class LLMProviderConfig:
    api_key: str
    default_model: str

@dataclass
class Config:
    def __init__(self):
        self.llm_providers = {}

def load_config():
    if not os.path.exists("promptvc.yaml"):
        raise FileNotFoundError("Config file not found. Run 'promptvc init' first.")
    
    yaml = YAML()
    with open("promptvc.yaml", "r") as f:
        data = yaml.load(f)
    
    if not data:
        raise ValueError("Empty config file")
    
    if "llm_providers" not in data:
        raise ValueError("Missing llm_providers section")
    
    config = Config()
    providers = data["llm_providers"]
    if providers is None:
        providers = {}
        
    for name, provider in providers.items():
        config.llm_providers[name] = LLMProviderConfig(
            api_key=provider["api_key"],
            default_model=provider["default_model"]
        )
    
    return config