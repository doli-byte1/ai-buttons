"""Provider registry for AI chat interfaces."""

PROVIDERS = {
    "chatgpt": {
        "label": "ChatGPT",
        "url": "https://chat.openai.com/?q={q}",
        "color": "#10a37f",
        "icon": "&#x2B21;",
        "order": 1,
    },
    "perplexity": {
        "label": "Perplexity",
        "url": "https://www.perplexity.ai/search/new?q={q}",
        "color": "#20808d",
        "icon": "&#x25CE;",
        "order": 2,
    },
    "claude": {
        "label": "Claude",
        "url": "https://claude.ai/new?q={q}",
        "color": "#d97706",
        "icon": "&#x25C8;",
        "order": 3,
    },
    "gemini": {
        "label": "Gemini",
        "url": "https://gemini.google.com/app?query={q}",
        "color": "#4285f4",
        "icon": "&#x2726;",
        "order": 4,
    },
    "grok": {
        "label": "Grok",
        "url": "https://x.com/i/grok?text={q}",
        "color": "#000000",
        "icon": "&#x1D54F;",
        "order": 5,
    },
    "copilot": {
        "label": "Copilot",
        "url": "https://copilot.microsoft.com/?q={q}",
        "color": "#7b2ff2",
        "icon": "&#x2B22;",
        "order": 6,
    },
    "meta": {
        "label": "Meta AI",
        "url": "https://www.meta.ai/?q={q}",
        "color": "#0668E1",
        "icon": "&#x25C9;",
        "order": 7,
    },
    "deepseek": {
        "label": "DeepSeek",
        "url": "https://chat.deepseek.com/?q={q}",
        "color": "#4d6bfe",
        "icon": "&#x25C6;",
        "order": 8,
    },
    "mistral": {
        "label": "Mistral",
        "url": "https://chat.mistral.ai/chat?q={q}",
        "color": "#ff7000",
        "icon": "&#x25B2;",
        "order": 9,
    },
    "googleai": {
        "label": "Google AI",
        "url": "https://www.google.com/search?udm=50&q={q}",
        "color": "#ea4335",
        "icon": "G",
        "order": 10,
    },
}

DEFAULT_PROVIDERS = [
    "chatgpt",
    "perplexity",
    "claude",
    "gemini",
    "grok",
    "copilot",
    "meta",
    "deepseek",
    "mistral",
    "googleai",
]
