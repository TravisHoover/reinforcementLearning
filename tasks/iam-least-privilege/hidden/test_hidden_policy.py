import pytest

from scripts.policy_sim import _as_list, is_allowed, load, statements

A = "123456789012"
ECR = f"arn:aws:ecr:us-east-1:{A}"
ECS = f"arn:aws:ecs:us-east-1:{A}"
IAM = f"arn:aws:iam::{A}"
LOGS = f"arn:aws:logs:us-east-1:{A}"

REQUIRED = [
    ("ecr:GetAuthorizationToken", "*"),
    *[(f"ecr:{a}", f"{ECR}:repository/core-api") for a in (
        "BatchCheckLayerAvailability", "InitiateLayerUpload", "UploadLayerPart",
        "CompleteLayerUpload", "PutImage", "BatchGetImage")],
    ("ecs:RegisterTaskDefinition", "*"),
    ("ecs:DescribeTaskDefinition", "*"),
    ("ecs:UpdateService", f"{ECS}:service/prod/core-api"),
    ("ecs:DescribeServices", f"{ECS}:service/prod/core-api"),
    ("iam:PassRole", f"{IAM}:role/core-api-task"),
    ("iam:PassRole", f"{IAM}:role/core-api-execution"),
    ("logs:CreateLogStream", f"{LOGS}:log-group:/ecs/core-api:log-stream:ecs/web/0f3a"),
    ("logs:PutLogEvents", f"{LOGS}:log-group:/ecs/core-api:log-stream:ecs/web/0f3a"),
]

FORBIDDEN = [
    ("iam:CreateUser", f"{IAM}:user/deploy-bot"),
    ("iam:CreateAccessKey", f"{IAM}:user/deploy-bot"),
    ("iam:AttachRolePolicy", f"{IAM}:role/core-api-task"),
    ("iam:PutRolePolicy", f"{IAM}:role/core-api-execution"),
    ("iam:PassRole", f"{IAM}:role/admin"),
    ("sts:AssumeRole", f"{IAM}:role/admin"),
    ("ecr:PutImage", f"{ECR}:repository/billing-api"),
    ("ecr:DeleteRepository", f"{ECR}:repository/core-api"),
    ("ecr:SetRepositoryPolicy", f"{ECR}:repository/core-api"),
    ("ecs:UpdateService", f"{ECS}:service/prod/billing-api"),
    ("ecs:UpdateService", f"{ECS}:service/staging/core-api"),
    ("ecs:DeleteService", f"{ECS}:service/prod/core-api"),
    ("ecs:DeleteCluster", f"{ECS}:cluster/prod"),
    ("ecs:RunTask", "*"),
    ("logs:DeleteLogGroup", f"{LOGS}:log-group:/ecs/core-api"),
    ("logs:PutLogEvents", f"{LOGS}:log-group:/ecs/billing-api:log-stream:x"),
    ("s3:GetObject", "arn:aws:s3:::prod-backups/db.dump"),
    ("secretsmanager:GetSecretValue", f"arn:aws:secretsmanager:us-east-1:{A}:secret:prod/db-AbCdEf"),
    ("kms:Decrypt", "*"),
    ("ec2:TerminateInstances", "*"),
]


@pytest.mark.parametrize("action,resource", REQUIRED)
def test_required_permissions_are_granted(action, resource):
    assert is_allowed(load(), action, resource)


@pytest.mark.parametrize("action,resource", FORBIDDEN)
def test_everything_else_is_denied(action, resource):
    assert not is_allowed(load(), action, resource)


def test_no_wildcard_actions_or_not_action_allows():
    for s in statements(load()):
        if s["Effect"] != "Allow":
            continue
        assert "NotAction" not in s and "NotResource" not in s, s
        for action in _as_list(s["Action"]):
            assert action != "*" and not action.endswith(":*"), action


def test_unscoped_resources_only_where_required():
    unscoped_ok = {"ecr:getauthorizationtoken", "ecs:registertaskdefinition", "ecs:describetaskdefinition"}
    for s in statements(load()):
        if s["Effect"] == "Allow" and "*" in _as_list(s["Resource"]):
            assert {a.lower() for a in _as_list(s["Action"])} <= unscoped_ok, s
