# Deploy pipeline: AWS permissions

Account `123456789012`, region `us-east-1`. The pipeline builds the `core-api`
image, pushes it to ECR, registers a new task definition, and rolls the
production ECS service.

| Actions | Resources |
|---|---|
| `ecr:GetAuthorizationToken` | `*` (this action does not support resource-level permissions) |
| `ecr:BatchCheckLayerAvailability`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`, `ecr:BatchGetImage` | `arn:aws:ecr:us-east-1:123456789012:repository/core-api` |
| `ecs:RegisterTaskDefinition`, `ecs:DescribeTaskDefinition` | `*` (these actions do not support resource-level permissions) |
| `ecs:UpdateService`, `ecs:DescribeServices` | `arn:aws:ecs:us-east-1:123456789012:service/prod/core-api` |
| `iam:PassRole` | `arn:aws:iam::123456789012:role/core-api-task`, `arn:aws:iam::123456789012:role/core-api-execution` |
| `logs:CreateLogStream`, `logs:PutLogEvents` | `arn:aws:logs:us-east-1:123456789012:log-group:/ecs/core-api:*` |
