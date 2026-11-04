from pathlib import Path

from scripts.dockerfile import copy_sources, instructions


def test_dependencies_install_before_source_is_copied():
    steps = instructions()
    install = next(i for i, (kw, args) in enumerate(steps) if kw == "RUN" and "pip install" in args)
    copies_before = [args for kw, args in steps[:install] if kw == "COPY"]
    assert copies_before, "requirements.txt must be copied before pip install"
    for args in copies_before:
        assert copy_sources(args) == ["requirements.txt"], args


def test_dockerignore_exists():
    assert Path(".dockerignore").exists()
