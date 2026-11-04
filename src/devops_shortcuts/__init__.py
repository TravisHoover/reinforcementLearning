"""Do coding agents take shortcuts on realistic DevOps tasks?

An Inspect eval: each task is a small repository with a realistic infrastructure
problem, visible tests the agent can run, hidden tests it can't see, and static
integrity checks that look for the shortcuts DevOps work invites (editing tests,
`continue-on-error`, `|| true`, skip markers, code that detects it is under test).

Run it with `inspect eval src/devops_shortcuts/tasks.py`.
"""
