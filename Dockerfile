# Super simple OpenClaw on Google Cloud Run
FROM node:20-alpine

# Install git FIRST (required for npm install)
RUN apk add --no-cache git

# Install OpenClaw
RUN npm install -g openclaw

# Set environment
ENV PORT=8080

# Start OpenClaw
CMD ["openclaw", "gateway", "--port", "8080", "--bind", "0.0.0.0"]