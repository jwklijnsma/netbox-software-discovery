FROM python:3.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY netbox_software_agent ./netbox_software_agent
RUN pip install --no-cache-dir "httpx>=0.27" "psutil>=6.0" && pip install --no-cache-dir --no-deps .
USER 10001:10001
ENTRYPOINT ["netbox-software-agent"]
