from typing import Any

import questionary

from daydream.config.utils import Config, PluginSettings
from daydream.plugins.base import Plugin
from daydream.utils import classproperty


class LlmPlugin(Plugin):
    """A plugin for configuring LLM models."""

    def __init__(
        self,
        *args: Any,
        model: str,
        api_key: str,
        temperature: float,
        max_tokens: int,
        cache: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.cache = cache

    @classproperty
    def default_plugin_settings(cls) -> PluginSettings:
        return {
            "model": "openai/gpt-4o-mini",
            "api_key": "",
            "temperature": 0,
            "max_tokens": 8192,
            "cache": True,
        }

    async def interactive_configure(self, cfg: Config) -> PluginSettings:
        """Interactive wizard for configuring the settings of this plugin."""
        defaults = self.default_plugin_settings

        return {
            "model": await questionary.text("Model", default=defaults["model"]).unsafe_ask_async(),
            "api_key": await questionary.password(
                "API key",
                default=defaults["api_key"],
            ).unsafe_ask_async(),
            "temperature": float(
                await questionary.text(
                    "Model temperature (any float between 0 and 2)",
                    default=str(defaults["temperature"]),
                    validate=lambda v: v.replace(".", "").isdigit() and 0 <= float(v) <= 2,
                ).unsafe_ask_async()
            ),
            "max_tokens": int(
                await questionary.text(
                    "Maximum number of tokens to generate for each response",
                    default=str(defaults["max_tokens"]),
                    validate=lambda v: v.isdigit() and 0 < int(v) <= 8192,
                ).unsafe_ask_async()
            ),
            "cache": await questionary.confirm(
                "Enable caching of responses",
                default=defaults["cache"],
            ).unsafe_ask_async(),
        }
