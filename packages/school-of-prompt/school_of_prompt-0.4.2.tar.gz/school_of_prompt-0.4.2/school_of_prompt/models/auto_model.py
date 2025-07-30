"""
Auto model creation with smart defaults.
"""

from typing import Any, Dict, Union

from ..core.simple_interfaces import SimpleModel


def auto_create_model(
    model: Union[str, Dict[str, Any], SimpleModel], api_key: str
) -> SimpleModel:
    """
    Auto-create model with smart defaults.

    Args:
        model: Model name, config dict, or custom model instance
        api_key: API key for the model

    Returns:
        SimpleModel instance
    """

    if isinstance(model, SimpleModel):
        return model

    if isinstance(model, str):
        # Simple model name - use defaults
        return _create_openai_model(model, api_key)

    if isinstance(model, dict):
        # Model config dict
        provider = model.get("provider", "openai")
        name = model.get("name", "gpt-3.5-turbo")

        if provider == "openai":
            return _create_openai_model(name, api_key, **model)
        elif provider == "anthropic":
            return _create_anthropic_model(name, api_key, **model)
        else:
            raise ValueError(f"Unsupported model provider: {provider}")

    raise ValueError(f"Unsupported model type: {type(model)}")


def _create_openai_model(name: str, api_key: str, **kwargs) -> SimpleModel:
    """Create OpenAI model with smart defaults."""

    try:
        import openai
    except ImportError:
        raise ImportError("openai package required. Install with: pip install openai")

    client = openai.OpenAI(api_key=api_key)

    # Extract model parameters
    temperature = kwargs.get("temperature", 0.0)
    max_tokens = kwargs.get("max_tokens", 150)

    # Detect chat models vs completion models
    chat_models = [
        'gpt-3.5-turbo', 'gpt-4', 'gpt-4o', 'gpt-4-turbo', 'gpt-4o-mini',
        'gpt-4-turbo-preview', 'gpt-4-vision-preview', 'gpt-3.5-turbo-instruct'
    ]
    
    # Check if this is a chat model (most models now are)
    is_chat_model = any(chat_model in name.lower() for chat_model in chat_models)
    
    # Special case: gpt-3.5-turbo-instruct is actually a completion model
    if 'gpt-3.5-turbo-instruct' in name.lower():
        is_chat_model = False

    def generate_func(prompt: str) -> str:
        try:
            if is_chat_model:
                # Use chat completions endpoint for modern models
                response = client.chat.completions.create(
                    model=name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
            else:
                # Use legacy completions endpoint for older models
                response = client.completions.create(
                    model=name,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    return SimpleModel(generate_func)


def _create_anthropic_model(name: str, api_key: str, **kwargs) -> SimpleModel:
    """Create Anthropic model with smart defaults."""

    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package required. Install with: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Extract model parameters
    temperature = kwargs.get("temperature", 0.0)
    max_tokens = kwargs.get("max_tokens", 150)

    def generate_func(prompt: str) -> str:
        try:
            response = client.completions.create(
                model=name,
                prompt=prompt,
                temperature=temperature,
                max_tokens_to_sample=max_tokens,
            )
            return response.completion.strip()
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    return SimpleModel(generate_func)
