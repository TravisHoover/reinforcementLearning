from scripts.policy_sim import is_allowed, load

ACCOUNT = "123456789012"
REPO = f"arn:aws:ecr:us-east-1:{ACCOUNT}:repository/core-api"
SERVICE = f"arn:aws:ecs:us-east-1:{ACCOUNT}:service/prod/core-api"


def test_pipeline_can_push_and_deploy():
    policy = load()
    assert is_allowed(policy, "ecr:GetAuthorizationToken", "*")
    assert is_allowed(policy, "ecr:PutImage", REPO)
    assert is_allowed(policy, "ecs:RegisterTaskDefinition", "*")
    assert is_allowed(policy, "ecs:UpdateService", SERVICE)
    assert is_allowed(policy, "iam:PassRole", f"arn:aws:iam::{ACCOUNT}:role/core-api-task")


def test_pipeline_cannot_create_iam_users():
    assert not is_allowed(load(), "iam:CreateUser", f"arn:aws:iam::{ACCOUNT}:user/attacker")
