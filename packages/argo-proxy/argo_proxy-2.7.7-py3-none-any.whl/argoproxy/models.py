# Model definitions with primary names as keys and aliases as strings or lists
import asyncio
import fnmatch
import json
import urllib.request
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Set, Tuple

from loguru import logger
from pydantic import BaseModel
from tqdm.asyncio import tqdm_asyncio

from .config import ArgoConfig, _get_yes_no_input_with_timeout
from .utils.transports import validate_api_async

DEFAULT_TIMEOUT = 30


# Create flattened mappings for lookup
def flatten_mapping(mapping: Dict[str, Any]) -> Dict[str, str]:
    flat = {}
    for model, aliases in mapping.items():
        if isinstance(aliases, str):
            flat[aliases] = model
        else:
            for alias in aliases:
                flat[alias] = model
    return flat


# Default models fallback
_DEFAULT_CHAT_MODELS = flatten_mapping(
    {
        # openai
        "gpt35": "argo:gpt-3.5-turbo",
        "gpt35large": "argo:gpt-3.5-turbo-16k",
        "gpt4": "argo:gpt-4",
        "gpt4large": "argo:gpt-4-32k",
        "gpt4turbo": "argo:gpt-4-turbo",
        "gpt4o": "argo:gpt-4o",
        "gpt4olatest": "argo:gpt-4o-latest",
        "gpto1mini": ["argo:gpt-o1-mini", "argo:o1-mini"],
        "gpto3mini": ["argo:gpt-o3-mini", "argo:o3-mini"],
        "gpto1": ["argo:gpt-o1", "argo:o1"],
        "gpto1preview": ["argo:gpt-o1-preview", "argo:o1-preview"],  # about to retire
        "gpto3": ["argo:gpt-o3", "argo:o3"],
        "gpto4mini": ["argo:gpt-o4-mini", "argo:o4-mini"],
        "gpt41": "argo:gpt-4.1",
        "gpt41mini": "argo:gpt-4.1-mini",
        "gpt41nano": "argo:gpt-4.1-nano",
        # gemini
        "gemini25pro": "argo:gemini-2.5-pro",
        "gemini25flash": "argo:gemini-2.5-flash",
        # claude
        "claudeopus4": ["argo:claude-opus-4", "argo:claude-4-opus"],
        "claudesonnet4": ["argo:claude-sonnet-4", "argo:claude-4-sonnet"],
        "claudesonnet37": ["argo:claude-sonnet-3.7", "argo:claude-3.7-sonnet"],
        "claudesonnet35v2": ["argo:claude-sonnet-3.5-v2", "argo:claude-3.5-sonnet-v2"],
    }
)

_EMBED_MODELS = flatten_mapping(
    {
        "ada002": "argo:text-embedding-ada-002",
        "v3small": "argo:text-embedding-3-small",
        "v3large": "argo:text-embedding-3-large",
    }
)


def filter_model_by_patterns(
    model_dict: Dict[str, str], patterns: Set[str]
) -> List[str]:
    """Filter model_dict values (model_id) by given fnmatch patterns,
    returning both the model_name (key) and model_id (value) for matches."""
    matching = set()
    for model_name, model_id in model_dict.items():
        if any(fnmatch.fnmatch(model_id, pattern) for pattern in patterns):
            matching.add(model_name)
            matching.add(model_id)
    return sorted(matching)


# any models that unable to handle system prompt
NO_SYS_MSG_PATTERNS: Set[str] = {
    "*o1preview",  # Explicitly matches gpto1preview
    "*o1mini",  # Explicitly matches gpto1mini
}

NO_SYS_MSG_MODELS = filter_model_by_patterns(
    _DEFAULT_CHAT_MODELS,
    NO_SYS_MSG_PATTERNS,
)


# any models that only able to handle single system prompt and no system prompt at all
OPTION_2_INPUT_PATTERNS: Set[str] = set()
# Commented out patterns:
# "*gemini*",  # Matches any model name starting with 'gemini'
# "*claude*",  # Matches any model name starting with 'claude'
# "gpto3",
# "gpto4*",
# "gpt41*",

OPTION_2_INPUT_MODELS = filter_model_by_patterns(
    _DEFAULT_CHAT_MODELS,
    OPTION_2_INPUT_PATTERNS,
)

# any models that supports native tool call
NATIVE_TOOL_CALL_PATTERNS: Set[str] = {
    "*o1",
    "*o3*",
    "*o4*",
}

NATIVE_TOOL_CALL_MODELS = filter_model_by_patterns(
    _DEFAULT_CHAT_MODELS,
    NATIVE_TOOL_CALL_PATTERNS,
)

TIKTOKEN_ENCODING_PREFIX_MAPPING = {
    "gpto": "o200k_base",  # o-series
    "gpt4o": "o200k_base",  # gpt-4o
    # this order need to be preserved to correctly parse mapping
    "gpt4": "cl100k_base",  # gpt-4 series
    "gpt3": "cl100k_base",  # gpt-3 series
    "ada002": "cl100k_base",  # embedding
    "v3": "cl100k_base",  # embedding
}


class Model(BaseModel):
    id: str
    model_name: str


class OpenAIModel(BaseModel):
    id: str
    internal_name: str
    object: Literal["model"] = "model"
    created: int = int(datetime.now().timestamp())
    owned_by: str = "argo"


GPT_O_PATTERN = "gpto*"
CLAUDE_PATTERN = "claude*"


def produce_argo_model_list(upstream_models: List[Model]) -> Dict[str, str]:
    """
    Generates a dictionary mapping standardized Argo model identifiers to their corresponding IDs.

    Args:
        upstream_models (List[Model]): A list of Model objects containing `model_name` and `id`.

    Returns:
        Dict[str, str]: A dictionary where keys are formatted Argo model identifiers
                        (e.g., "argo:gpt-4o", "argo:claude-4-opus") and values are model IDs.

    The method creates special cases for specific models like GPT-O and Claude, adding additional granularity
    in the naming convention. It appends regular model mappings under the `argo:` prefix for all models.
    """
    argo_models = {}
    for model in upstream_models:
        model.model_name = model.model_name.replace(" ", "-").lower()

        if fnmatch.fnmatch(model.id, GPT_O_PATTERN):
            # special: argo:gpt-o1
            argo_models[f"argo:gpt-{model.model_name}"] = model.id

        elif fnmatch.fnmatch(model.id, CLAUDE_PATTERN):
            _, codename, gen_num, *version = model.model_name.split("-")
            if version:
                # special: argo:claude-3.5-sonnet-v2
                argo_models[f"argo:claude-{gen_num}-{codename}-{version[0]}"] = model.id
            else:
                # special: argo:claude-4-opus
                argo_models[f"argo:claude-{gen_num}-{codename}"] = model.id

        # regular: argo:gpt-4o, argo:o1 or argo:claude-opus-4
        argo_models[f"argo:{model.model_name}"] = model.id

    return argo_models


def get_upstream_model_list(url: str) -> Dict[str, str]:
    """
    Fetches the list of available models from the upstream server.
    Args:
        url (str): The URL of the upstream server.
    Returns:
       Dict[str, Any]: A dictionary containing the list of available models.
    """
    try:
        with urllib.request.urlopen(url) as response:
            raw_data = json.loads(response.read().decode())["data"]
            models = [Model(**model) for model in raw_data]

            argo_models = produce_argo_model_list(models)

            return argo_models
    except Exception as e:
        logger.error(f"Error fetching model list from {url}")
        logger.warning("Using built-in model list.")
        return _DEFAULT_CHAT_MODELS


async def _check_model_streamability(
    model_id: str,
    stream_url: str,
    non_stream_url: str,
    user: str,
    payload: Dict[str, Any],
) -> Tuple[str, Optional[bool]]:
    """Check if a model is streamable using model_id."""
    payload_copy = payload.copy()
    payload_copy["model"] = model_id

    try:
        # First, try streaming
        await validate_api_async(
            stream_url,
            user,
            payload_copy,
            timeout=DEFAULT_TIMEOUT,
        )
        return (model_id, True)
    except Exception:
        # If streaming fails, try non-streaming
        try:
            await validate_api_async(
                non_stream_url,
                user,
                payload_copy,
                timeout=DEFAULT_TIMEOUT,
            )
            return (model_id, False)
        except Exception:
            logger.error(f"All attempts failed for model ID: {model_id}")
            return (model_id, None)


def _categorize_results(
    results: List[Tuple[str, Optional[bool]]], model_mapping: Dict[str, str]
) -> Tuple[List[str], List[str], List[str]]:
    """Categorize model check results into streamable/non-streamable/unavailable.
    Maps results back to all aliases using the model_mapping."""
    streamable = set()
    non_streamable = set()
    unavailable = set()

    # Create reverse mapping from model_id to all its aliases
    reverse_mapping = {}
    for alias, model_id in model_mapping.items():
        reverse_mapping.setdefault(model_id, []).append(alias)

    for model_id, status in results:
        aliases = reverse_mapping.get(model_id, [model_id])
        if status is True:
            streamable.update(aliases)
            non_streamable.update(aliases)
        elif status is False:
            non_streamable.update(aliases)
        elif status is None:
            unavailable.update(aliases)

    if unavailable:
        logger.warning(f"Unavailable models: {unavailable}")
        if _get_yes_no_input_with_timeout(
            "Do you want to keep using them? It might be a temporary issue. [Y/n]",
            timeout=5,
        ):
            non_streamable.update(unavailable)
            unavailable.clear()
        else:
            logger.error(
                "Proceeding without unavailable models. Subsequent calls to these models will be replaced with argo:gpt-4o"
            )

    return (
        sorted(list(streamable)),
        sorted(list(non_streamable)),
        sorted(list(unavailable)),
    )


async def determine_models_availability(
    stream_url: str, non_stream_url: str, user: str, model_list: Dict[str, str]
) -> Tuple[List[str], List[str], List[str]]:
    """
    Asynchronously checks which models are streamable.
    Args:
        stream_url: URL for streaming API endpoint
        non_stream_url: URL for non-streaming API endpoint
        user: User identifier
        model_list: Dictionary mapping model aliases to their IDs
    Returns:
        Tuple of (streamable_models, non_streamable_models, unavailable_models)
        where each list contains all aliases for the models
    """
    payload = {
        "model": None,
        "messages": [{"role": "user", "content": "What are you?"}],
    }

    # Get unique model IDs to check (avoid duplicate checks for same ID)
    unique_model_ids = set(model_list.values())
    tasks = [
        _check_model_streamability(model_id, stream_url, non_stream_url, user, payload)
        for model_id in unique_model_ids
    ]

    # Run all checks concurrently, showing a progress bar
    results = []
    for coro in tqdm_asyncio.as_completed(
        tasks, total=len(tasks), desc="Checking models"
    ):
        result = await coro
        results.append(result)

    return _categorize_results(results, model_list)


class ModelRegistry:
    def __init__(self, config: ArgoConfig):
        self._chat_models: Dict[str, str] = {}
        self._no_sys_msg_models = NO_SYS_MSG_MODELS
        self._option_2_input_models = OPTION_2_INPUT_MODELS
        self._native_tool_call_models = NATIVE_TOOL_CALL_MODELS

        # these are model_name to failed_count mappings
        self._streamable_models: Dict[str, int] = defaultdict(lambda: 0)
        self._non_streamable_models: Dict[str, int] = defaultdict(lambda: 0)
        self._unavailable_models: Dict[str, int] = defaultdict(lambda: 0)

        # internal state
        self._last_updated: Optional[datetime] = None
        self._refresh_task = None
        self._config = config

    async def initialize(self):
        """Initialize model registry with upstream data"""

        # Initial availability check
        try:
            await self.refresh_availability()
        except Exception as e:
            logger.error(f"Initial availability check failed: {str(e)}")

        # # Start periodic refresh (default 24h)
        # self._refresh_task = asyncio.create_task(
        #     self._periodic_refresh(interval_hours=24)
        # )

    async def refresh_availability(self, real_test: bool = False):
        """Refresh model availability status"""
        if not self._config:
            raise ValueError("Failed to load valid configuration")

        # Initial model list fetch
        self._chat_models = get_upstream_model_list(self._config.argo_model_url)
        logger.info(f"Initialized model registry with {len(self._chat_models)} models")

        try:
            if real_test:
                (
                    streamable,
                    non_streamable,
                    unavailable,
                ) = await determine_models_availability(
                    self._config.argo_stream_url,
                    self._config.argo_url,
                    self._config.user,
                    self.available_chat_models,
                )
            else:
                # assume all of them are available and streamable, for now, disable them on the fly if failed with user query
                streamable = self.available_chat_models.keys()
                non_streamable = self.available_chat_models.keys()
                unavailable = []

            for name in streamable:
                self._streamable_models[name]
            for name in non_streamable:
                self._non_streamable_models[name]
            for name in unavailable:
                self._unavailable_models[name]
            self._last_updated = datetime.now()

            # Update model lists based on model IDs
            self._no_sys_msg_models = filter_model_by_patterns(
                self.available_chat_models, NO_SYS_MSG_PATTERNS
            )

            self._option_2_input_models = filter_model_by_patterns(
                self.available_chat_models, OPTION_2_INPUT_PATTERNS
            )

            self._native_tool_call_models = filter_model_by_patterns(
                self.available_chat_models, NATIVE_TOOL_CALL_PATTERNS
            )

            logger.info("Model availability refreshed successfully")
        except Exception as e:
            logger.error(f"Failed to refresh model availability: {str(e)}")
            if not self._last_updated:
                self._chat_models = _DEFAULT_CHAT_MODELS
                logger.warning("Falling back to default model list")

    # async def _periodic_refresh(self, interval_hours: float):
    #     """Background task for periodic refresh"""
    #     while True:
    #         await asyncio.sleep(interval_hours * 3600)
    #         try:
    #             await self.refresh_availability()
    #         except Exception as e:
    #             logger.error(f"Periodic refresh failed: {str(e)}")

    async def manual_refresh(self):
        """Trigger manual refresh of model data"""
        try:
            await self.refresh_availability(real_test=True)
        except Exception as e:
            logger.error(f"Manual refresh failed: {str(e)}")

    def resolve_model_name(
        self,
        model_name: str,
        model_type: Literal["chat", "embed"],
    ) -> str:
        """
        Resolves a model name to its primary model name using the flattened model mapping.

        Args:
            model_name: The input model name to resolve
            model_type: The type of model to resolve (chat or embed)

        Returns:
            The resolved primary model name or default_model if no match found
        """

        # directly pass in resolved model_id
        if model_name in self.available_models.values():
            return model_name

        # Check if input exists in the flattened mapping
        if model_name in self.available_models:
            return self.available_models[model_name]
        else:
            if model_type == "chat":
                default_model = "argo:gpt-4o"
            elif model_type == "embed":
                default_model = "argo:text-embedding-3-small"
            return self.available_models[default_model]

    def as_openai_list(self) -> Dict[str, Any]:
        # Mock data for available models
        model_data: Dict[str, Any] = {"object": "list", "data": []}  # type: ignore

        # Populate the models data with the combined models
        for model_name, model_id in self.available_models.items():
            model_data["data"].append(
                OpenAIModel(id=model_name, internal_name=model_id).model_dump()
            )

        return model_data

    def flag_as_non_streamable(self, model_name: str):
        self._streamable_models.pop(
            model_name, 0
        )  # Remove if present, ignore otherwise
        self._non_streamable_models[model_name]

    def flag_as_streamable(self, model_name: str):
        self._non_streamable_models.pop(model_name, 0)
        self._streamable_models[model_name]

    def flag_as_unavailable(self, model_name: str):
        self._unavailable_models[model_name]
        self._streamable_models.pop(model_name, 0)
        self._non_streamable_models.pop(model_name, 0)

    @property
    def available_chat_models(self):
        return self._chat_models or _DEFAULT_CHAT_MODELS

    @property
    def available_embed_models(self):
        return _EMBED_MODELS

    @property
    def available_models(self):
        return {**self.available_chat_models, **self.available_embed_models}

    @property
    def unavailable_models(self):
        return list(self._unavailable_models.keys())

    @property
    def streamable_models(self):
        return list(self._streamable_models.keys())

    @property
    def non_streamable_models(self):
        return list(self._non_streamable_models.keys()) or list(
            _DEFAULT_CHAT_MODELS.keys()
        )

    @property
    def no_sys_msg_models(self):
        return self._no_sys_msg_models or NO_SYS_MSG_MODELS

    @property
    def option_2_input_models(self):
        return self._option_2_input_models or OPTION_2_INPUT_MODELS

    @property
    def native_tool_call_models(self):
        return self._native_tool_call_models or NATIVE_TOOL_CALL_MODELS


if __name__ == "__main__":
    import asyncio

    from .config import load_config

    config, _ = load_config(verbose=False)
    if config is None:
        raise ValueError("Config is None")

    model_registry = ModelRegistry(config)
    asyncio.run(model_registry.initialize())

    logger.info(f"Available stream models: {model_registry.streamable_models}")
    logger.info(f"Available non-stream models: {model_registry.non_streamable_models}")
    logger.info(f"Unavailable models: {model_registry.unavailable_models}")

    logger.info(f"Native tool call models: {model_registry.native_tool_call_models}")
