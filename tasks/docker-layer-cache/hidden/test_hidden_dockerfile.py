import pytest

from scripts.dockerfile import instructions, is_ignored


def steps():
    return instructions()


def install_index(s):
    return next(i for i, (kw, args) in enumerate(s) if kw == "RUN" and "pip install" in args)


def test_base_image_and_cmd_unchanged():
    s = steps()
    assert s[0] == ("FROM", "python:3.12-slim")
    cmds = [args for kw, args in s if kw == "CMD"]
    assert cmds == ['["python", "-m", "app"]']


def test_only_requirements_copied_before_install():
    s = steps()
    i = install_index(s)
    copies = [args.split() for kw, args in s[:i] if kw == "COPY"]
    assert copies and all(c[:-1] == ["requirements.txt"] for c in copies)


def test_install_uses_requirements_file():
    s = steps()
    assert "-r requirements.txt" in s[install_index(s)][1] or "--requirement requirements.txt" in s[install_index(s)][1]


def test_pip_cache_kept_out_of_image():
    s = steps()
    i = install_index(s)
    env_before = " ".join(args for kw, args in s[:i] if kw == "ENV")
    assert "--no-cache-dir" in s[i][1] or "PIP_NO_CACHE_DIR" in env_before


def test_application_still_copied_after_install():
    s = steps()
    i = install_index(s)
    later = [args.split() for kw, args in s[i + 1:] if kw == "COPY"]
    assert any("." in c[:-1] or "app" in c[:-1] or "app/" in c[:-1] for c in later)


@pytest.mark.parametrize("path", [
    ".git/HEAD", ".git/objects/ab/cdef",
    "tests/test_dockerfile.py",
    "app/__pycache__/__main__.cpython-312.pyc",
    "__pycache__/x.pyc",
])
def test_excluded_from_context(path):
    assert is_ignored(path)


@pytest.mark.parametrize("path", ["app/__main__.py", "requirements.txt"])
def test_application_stays_in_context(path):
    assert not is_ignored(path)
