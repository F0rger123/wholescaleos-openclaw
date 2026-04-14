# OpenClaw on Google Cloud Run
FROM node:22-alpine

# Install OpenClaw globally
RUN npm install -g openclaw

# Create workspace directory
RUN mkdir -p /app/workspace
WORKDIR /app/workspace

# Copy your workspace files
COPY . /app/workspace/

# Install Python dependencies
RUN apk add --no-cache python3 py3-pip
RUN pip3 install -r requirements.txt 2>/dev/null || echo "No requirements.txt"

# Set environment variables for cloud operation
ENV OPENCLAW_STATE_DIR=/app/state
ENV OPENCLAW_WORKSPACE=/app/workspace
ENV RUN_MODE=cloud

# Create state directory
RUN mkdir -p /app/state

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Start OpenClaw gateway
CMD ["openclaw", "gateway", "--port", "8080", "--bind", "0.0.0.0"]