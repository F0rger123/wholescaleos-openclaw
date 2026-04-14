# Correct OpenClaw Dockerfile for Cloud Run
FROM node:20-alpine

# Install git (required for npm install)
RUN apk add --no-cache git

# Install OpenClaw globally
RUN npm install -g openclaw

# Verify installation
RUN which openclaw && openclaw --version

# Create app directory
WORKDIR /app

# Set environment
ENV PORT=8080
ENV RUN_MODE=cloud

# Create startup script
RUN echo '#!/bin/sh\n\
echo "Starting OpenClaw gateway..."\n\
openclaw gateway --port $PORT --bind 0.0.0.0\n\
echo "OpenClaw started on port $PORT"' > /app/start.sh

RUN chmod +x /app/start.sh

# Health check (simple curl)
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Start OpenClaw
CMD ["/app/start.sh"]