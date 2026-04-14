# Minimal OpenClaw Dockerfile
FROM node:20-alpine

# Install git first
RUN apk add --no-cache git

# Install OpenClaw
RUN npm install -g openclaw

# Test installation
RUN openclaw --version

# Set port
ENV PORT=8080

# Simple command
CMD ["openclaw", "gateway", "--port", "8080", "--bind", "0.0.0.0"]