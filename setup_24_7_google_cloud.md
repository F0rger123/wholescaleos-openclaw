# 24/7 OpenClaw Setup on Google Cloud Run (FREE)

## **Why Google Cloud Run?**
- **Free tier:** 2 million requests/month
- **Always runs** (wakes on request)
- **Container-based** (easy deployment)
- **Cost:** ~$0 when idle

## **Setup Steps:**

### **1. Prerequisites**
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Login and create project
gcloud auth login
gcloud projects create openclaw-wholescaleos
gcloud config set project openclaw-wholescaleos
```

### **2. Enable APIs**
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### **3. Create Dockerfile**
```dockerfile
FROM node:22-alpine

# Install OpenClaw
RUN npm install -g openclaw

# Create workspace
RUN mkdir -p /app/workspace
WORKDIR /app/workspace

# Copy your workspace
COPY . /app/workspace/

# Start OpenClaw
CMD ["openclaw", "gateway", "--port", "8080", "--bind", "0.0.0.0"]
```

### **4. Deploy to Cloud Run**
```bash
# Build and deploy
gcloud run deploy openclaw \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 1

# Get URL
gcloud run services describe openclaw --format='value(status.url)'
```

## **Alternative: Railway.app (Easier)**
1. Sign up at railway.app (GitHub login)
2. Create new project
3. Connect GitHub repo
4. Add `Dockerfile`
5. Deploy (free $5 credit)

## **Alternative: Fly.io**
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch
fly launch --now
fly scale count 1
```

## **Keep Local + Cloud Hybrid**
- **Local:** Development, testing
- **Cloud:** 24/7 scheduled reports
- **Sync:** Git for workspace files

## **Cost Estimate:**
- **Google Cloud Run:** $0-$5/month
- **Railway:** $0 (free credit)
- **Fly.io:** $0 (free tier)
- **Always-on:** Your choice!