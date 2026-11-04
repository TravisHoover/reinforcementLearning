from pathlib import Path

from scripts.dockerfile import instructions


def first_index(steps, predicate):
    return next(i for i, step in enumerate(steps) if predicate(step))


def test_dependencies_install_before_source_is_copied():
    steps = instructions()
    install = first_index(steps, lambda s: s[0] == "RUN" and "pip install" in s[1])
    copies_before = [args for kw, args in steps[:install] if kw == "COPY"]
    assert copies_before, "requirements.txt must be copied before pip install"
    for args in copies_before:
        sources = args.split()[:-1]
        assert sources == ["requirements.txt"], args


def test_dockerignore_exists():
    assert Path(".dockerignore").exists()
