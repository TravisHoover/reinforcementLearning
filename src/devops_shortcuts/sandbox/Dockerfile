FROM python:3.12-slim

# tzdata: the release-window task needs IANA time zones.
RUN pip install --no-cache-dir pytest==8.3.5 pyyaml==6.0.2 tzdata==2025.2

# Two unprivileged accounts. The agent works as `agent` and can edit its
# workspace but not the Python installation. Graded test runs execute as
# `grader`, in private directories the agent can't read or write.
RUN useradd --create-home agent \
 && useradd --create-home grader \
 && mkdir /workspace \
 && chown agent:agent /workspace

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
