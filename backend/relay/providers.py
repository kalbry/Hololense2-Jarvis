"""
Model-agnostic LLM provider interface — Phase 6 of docs/BUILD_PLAN.md.

Add/enable providers by installing their SDK and filling in the relevant
class below. config.yaml's `provider:` key selects which one is used at
runtime — no code changes needed to switch providers day-to-day.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def get_response(self, prompt: str, history: list[dict]) -> str:
        """Return the assistant's reply text for the given prompt + history.

        history is a list of {"role": "user"|"assistant", "content": str}
        in chronological order (most recent last).
        """
        raise NotImplementedError


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        # pip install anthropic
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def get_response(self, prompt: str, history: list[dict]) -> str:
        messages = history + [{"role": "user", "content": prompt}]
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=messages,
        )
        return response.content[0].text


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        # pip install openai
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def get_response(self, prompt: str, history: list[dict]) -> str:
        messages = history + [{"role": "user", "content": prompt}]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        # pip install google-generativeai
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    async def get_response(self, prompt: str, history: list[dict]) -> str:
        # NOTE: google-generativeai's chat history format differs from
        # Claude/OpenAI's — this is a starting stub, adapt as needed once
        # you reach Phase 6.
        chat = self.model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text


class HermesProvider(LLMProvider):
    """Bridges to a self-hosted Hermes Agent gateway instead of calling an
    LLM API directly. Fill in once you've decided on Hermes's gateway
    protocol (see hermes-agent.org docs) — this is a placeholder shape.
    """

    def __init__(self, gateway_url: str, api_key: str | None = None):
        self.gateway_url = gateway_url
        self.api_key = api_key

    async def get_response(self, prompt: str, history: list[dict]) -> str:
        raise NotImplementedError(
            "Wire this up to your Hermes Agent gateway once Phase 6 is reached. "
            "See hermes-agent.org docs for the gateway API shape."
        )


def get_provider(config: dict) -> LLMProvider:
    provider_name = config.get("provider")
    provider_config = config.get("providers", {}).get(provider_name, {})

    if provider_name == "claude":
        return ClaudeProvider(**provider_config)
    elif provider_name == "openai":
        return OpenAIProvider(**provider_config)
    elif provider_name == "gemini":
        return GeminiProvider(**provider_config)
    elif provider_name == "hermes":
        return HermesProvider(**provider_config)
    else:
        raise ValueError(
            f"Unknown provider '{provider_name}'. Set `provider:` in "
            "config.yaml to one of: claude, openai, gemini, hermes."
        )
