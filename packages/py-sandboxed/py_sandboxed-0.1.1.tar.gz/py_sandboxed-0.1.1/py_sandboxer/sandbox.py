import ast
import builtins
import fnmatch
from types import SimpleNamespace

from .rules import filter_globals, load_ruleset
from .exceptions import SandboxViolation


def _prepare_modules(rules):
    allow = rules.get("allow", [])
    deny = rules.get("deny", [])
    modules = {}
    for pattern in allow:
        if "." in pattern:
            mod, attr_pat = pattern.split(".", 1)
            modules.setdefault(mod, []).append(attr_pat)
    safe_modules = {}
    for mod, pats in modules.items():
        try:
            m = __import__(mod)
        except ImportError:
            continue
        safe_mod = SimpleNamespace()
        for name in dir(m):
            full = f"{mod}.{name}"
            if any(fnmatch.fnmatch(name, p) for p in pats) and not any(
                fnmatch.fnmatch(full, dp) for dp in deny
            ):
                setattr(safe_mod, name, getattr(m, name))
        safe_modules[mod] = safe_mod
    return safe_modules


class SandboxGuard(ast.NodeVisitor):
    def __init__(self, block_import: bool = False, block_dunder: bool = False):
        self.block_import = block_import
        self.block_dunder = block_dunder

    def visit_Import(self, node):
        if self.block_import:
            raise SandboxViolation("Import statements not allowed")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if self.block_import:
            raise SandboxViolation("Import statements not allowed")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if (
            self.block_dunder
            and isinstance(node.attr, str)
            and node.attr.startswith("__")
        ):
            raise SandboxViolation("Dunder access not allowed")
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.block_import and isinstance(node.func, ast.Name):
            if node.func.id in {"__import__", "eval", "exec"}:
                raise SandboxViolation(f"{node.func.id} not allowed")
        self.generic_visit(node)


def guard_code(code: str, rules):
    if not rules.get("block_import") and not rules.get("block_dunder"):
        return
    tree = ast.parse(code, mode="exec")
    SandboxGuard(
        block_import=rules.get("block_import", False),
        block_dunder=rules.get("block_dunder", False),
    ).visit(tree)


def sandbox_eval(expr: str, config=None):
    rules = load_ruleset(config)
    guard_code(expr, rules)
    safe_globals = filter_globals(vars(builtins), rules)
    safe_globals.update(_prepare_modules(rules))
    try:
        return eval(expr, {"__builtins__": safe_globals})
    except Exception as exc:
        raise SandboxViolation(str(exc)) from exc


def sandbox_exec(code: str, config=None) -> dict:
    rules = load_ruleset(config)
    guard_code(code, rules)
    safe_globals = filter_globals(vars(builtins), rules)
    safe_globals.update(_prepare_modules(rules))
    local_ns = {}
    try:
        exec(code, {"__builtins__": safe_globals}, local_ns)
    except Exception as exc:
        raise SandboxViolation(str(exc)) from exc
    return local_ns
