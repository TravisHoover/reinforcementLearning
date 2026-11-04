FROM python:3.12-slim

# tzdata: the release-window task needs IANA time zones.
RUN pip install --no-cache-dir pytest==8.3.5 pyyaml==6.0.2 tzdata==2025.2

# The agent runs as an unprivileged user, so it can edit its workspace but not
# the Python installation the grader relies on.
RUN useradd --create-home agent \
 && mkdir /workspace \
 && chown agent:agent /workspace

WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]
