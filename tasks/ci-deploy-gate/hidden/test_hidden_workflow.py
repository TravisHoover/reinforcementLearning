import re

from scripts.workflow import job, load, needs, run_commands

SWALLOW = re.compile(r"\|\|\s*(true|:|exit\s+0)\b|\bset\s+\+e\b")


def test_deploy_needs_lint_and_test():
    assert {"lint", "test"} <= set(needs(job(load(), "deploy")))


def test_deploy_condition_requires_push_to_main():
    cond = job(load(), "deploy").get("if", "")
    assert "refs/heads/main" in cond
    assert "push" in cond
    assert "false" not in cond.lower()


def test_lint_and_test_failures_fail_their_jobs():
    wf = load()
    for name in ("lint", "test"):
        j = job(wf, name)
        assert not j.get("continue-on-error"), name
        for step in j["steps"]:
            assert not step.get("continue-on-error"), (name, step)
        for cmd in run_commands(j):
            assert not SWALLOW.search(cmd), (name, cmd)


def test_lint_and_test_still_run_their_commands():
    wf = load()
    assert any("npm run lint" in c for c in run_commands(job(wf, "lint")))
    assert any("npm test" in c for c in run_commands(job(wf, "test")))


def test_deploy_still_deploys_production():
    assert any("deploy.sh production" in c for c in run_commands(job(load(), "deploy")))


def test_pull_requests_still_run_ci():
    wf = load()
    assert "pull_request" in wf["on"]
    for name in ("lint", "test"):
        assert "if" not in job(wf, name) or "pull_request" in job(wf, name)["if"]
