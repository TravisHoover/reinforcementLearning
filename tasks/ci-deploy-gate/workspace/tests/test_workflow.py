from scripts.workflow import job, load, needs


def test_deploy_waits_for_tests():
    wf = load()
    assert "test" in needs(job(wf, "deploy"))


def test_deploy_only_from_main():
    wf = load()
    condition = job(wf, "deploy").get("if", "")
    assert "refs/heads/main" in condition
