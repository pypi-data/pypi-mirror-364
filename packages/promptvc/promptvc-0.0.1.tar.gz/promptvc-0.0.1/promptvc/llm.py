from promptvc.config import load_config
import openai
import anthropic

def call_openai(prompt_text):
    try:
        config = load_config()
        provider_config = config.llm_providers.get("openai")
        if not provider_config:
            return "Error: OpenAI configuration not found in promptvc.yaml"

        client = openai.OpenAI(api_key=provider_config.api_key)
        response = client.chat.completions.create(
            model=provider_config.default_model,
            messages=[{"role": "user", "content": prompt_text}]
        )
        
        if response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return "Error: Empty response from OpenAI."

    except Exception as e:
        return f"Error calling OpenAI: {e}"


def call_anthropic(prompt_text):
    try:
        config = load_config()
        provider_config = config.llm_providers.get("anthropic")
        if not provider_config:
            return "Error: Anthropic configuration not found in promptvc.yaml"

        client = anthropic.Anthropic(api_key=provider_config.api_key)
        response = client.messages.create(
            model=provider_config.default_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt_text}]
        )
        
        if response.content[0].text:
            return response.content[0].text
        else:
            return "Error: Empty response from Anthropic."

    except Exception as e:
        return f"Error calling Anthropic: {e}"