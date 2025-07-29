import fnmatch
from pathlib import Path
from typing import Dict, Union


PRESET_RULES = {
    "open": {"allow": ["*"], "deny": []},
    "math_only": {
        "allow": ["abs", "min", "max", "sum", "range", "math.*"],
        "deny": ["__import__"],
        "block_import": True,
    },
    "no_import": {"allow": ["*"], "deny": ["__import__"], "block_import": True},
    "no_import_no_traversal": {
        "allow": ["*"],
        "deny": ["__import__"],
        "block_import": True,
        "block_dunder": True,
    },
}


DEFAULT_PRESET = "open"


def load_ruleset(config: Union[Dict, str, None]) -> Dict:
    if config is None:
        return PRESET_RULES[DEFAULT_PRESET].copy()

    if isinstance(config, dict):
        rules = PRESET_RULES[DEFAULT_PRESET].copy()
        rules.update(config)
        return rules

    if isinstance(config, str) and config in PRESET_RULES:
        return PRESET_RULES[config].copy()

    config_path = Path(str(config))
    if config_path.is_file():
        import json
        with open(config_path) as fh:
            user_rules = json.load(fh)
        rules = PRESET_RULES[DEFAULT_PRESET].copy()
        rules.update(user_rules)
        return rules

    return PRESET_RULES[DEFAULT_PRESET].copy()


def filter_globals(globals_dict: Dict, rules: Dict) -> Dict:
    allowed = {}
    allow_patterns = rules.get("allow", [])
    deny_patterns = rules.get("deny", [])
    for name, obj in globals_dict.items():
        denied = any(fnmatch.fnmatch(name, pat) for pat in deny_patterns)
        allowed_match = any(fnmatch.fnmatch(name, pat) for pat in allow_patterns)
        if not denied and allowed_match:
            allowed[name] = obj
    return allowed
