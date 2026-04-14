# Simple OpenClaw on Google Cloud Run
FROM node:22-alpine

# Install OpenClaw
RUN npm install -g openclaw

# Create workspace
WORKDIR /app

# Set environment
ENV RUN_MODE=cloud

# Start OpenClaw
CMD ["openclaw", "gateway", "--port", "8080", "--bind", "0.0.0.0"]