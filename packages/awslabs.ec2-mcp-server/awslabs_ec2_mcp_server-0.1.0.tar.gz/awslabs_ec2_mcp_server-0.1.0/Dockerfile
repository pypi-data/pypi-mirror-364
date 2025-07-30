# Multi-stage build for AWS EC2 MCP Server
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FASTMCP_LOG_LEVEL=INFO

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r mcp && useradd -r -g mcp mcp

# Create working directory and set ownership
WORKDIR /app
RUN chown -R mcp:mcp /app

# Copy application from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=mcp:mcp . .

# Install the application
RUN pip install --no-cache-dir -e .

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/tmp && chown -R mcp:mcp /app/logs /app/tmp

# Switch to non-root user
USER mcp

# Expose the default MCP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import awslabs.ec2_mcp_server; print('OK')" || exit 1

# Set entrypoint
ENTRYPOINT ["python", "-m", "awslabs.ec2_mcp_server.server"]

# Labels for metadata
LABEL org.opencontainers.image.title="AWS EC2 MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for AWS EC2 management" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.vendor="Amazon Web Services" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.source="https://github.com/awslabs/mcp"