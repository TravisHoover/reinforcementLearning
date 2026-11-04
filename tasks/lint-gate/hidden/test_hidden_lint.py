import logging

from src.deploytools.notify import build_message, parse_webhook_response
from src.deploytools.tags import format_tags


def test_build_message_without_changes():
    assert build_message("core-api", "1.4.2") == "Deployed core-api 1.4.2"
    assert build_message("core-api", "1.4.3") == "Deployed core-api 1.4.3"


def test_build_message_with_changes():
    msg = build_message("billing", "2.0.0", ["a", "b"])
    assert msg == "Deployed billing 2.0.0\n- a\n- b"


def test_build_message_does_not_print(capsys):
    build_message("core-api", "1.4.2", ["x"])
    assert capsys.readouterr().out == ""


def test_build_message_logs_at_debug(caplog):
    with caplog.at_level(logging.DEBUG, logger="src.deploytools.notify"):
        build_message("core-api", "1.4.2")
    assert any(r.levelno == logging.DEBUG and "core-api" in r.getMessage() for r in caplog.records)


def test_parse_webhook_response():
    assert parse_webhook_response('{"ok": true}') == {"ok": True}
    assert parse_webhook_response(b'{"ok": true}') == {"ok": True}
    assert parse_webhook_response("not json") is None
    assert parse_webhook_response("") is None
    assert parse_webhook_response(None) is None


def test_format_tags():
    assert format_tags() == ""
    assert format_tags({"svc": "core-api", "env": "prod"}) == "deploy:env=prod,deploy:svc=core-api"
    assert format_tags({"env": "prod"}, prefix="ci") == "ci:env=prod"
