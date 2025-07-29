import pytest
from py_sandboxer import sandbox_eval, sandbox_exec, SandboxViolation


def test_open_allows_import():
    ns = sandbox_exec("import os\nval = os.name")
    assert ns["val"]


def test_math_only_allows_math():
    assert sandbox_eval("math.sqrt(9)", config="math_only") == 3


def test_math_only_blocks_import():
    with pytest.raises(SandboxViolation):
        sandbox_exec("import os", config="math_only")


def test_no_import_blocks_import():
    with pytest.raises(SandboxViolation):
        sandbox_exec("import os", config="no_import")


def test_no_import_no_traversal_blocks_dunder():
    with pytest.raises(SandboxViolation):
        sandbox_eval("(1).__class__", config="no_import_no_traversal")

