# OpenClaw on Google Cloud Run - Fixed version
FROM node:20-alpine

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    curl

# Install OpenClaw globally
RUN npm install -g openclaw

# Create workspace
WORKDIR /app

# Set environment
ENV NODE_ENV=production
ENV RUN_MODE=cloud
ENV PORT=8080

# Create a simple start script
RUN echo '#!/bin/sh\nopenclaw gateway --port 8080 --bind 0.0.0.0' > /app/start.sh
RUN chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start OpenClaw
CMD ["/app/start.sh"]