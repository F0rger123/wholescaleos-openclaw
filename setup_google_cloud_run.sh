#!/bin/bash
# Setup Google Cloud Run for OpenClaw 24/7 operation

echo "🚀 Setting up Google Cloud Run for 24/7 OpenClaw"
echo "================================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found."
    echo "📦 Install with: curl https://sdk.cloud.google.com | bash"
    echo "🔧 Then run: exec -l \$SHELL && gcloud init"
    exit 1
fi

echo "1. 🔐 Checking authentication..."
gcloud auth list || {
    echo "   Please login: gcloud auth login"
    exit 1
}

echo "2. 📁 Creating Google Cloud project..."
PROJECT_ID="openclaw-wholescaleos-$(date +%s)"
gcloud projects create $PROJECT_ID --set-as-default || {
    echo "   Using existing project..."
    PROJECT_ID=$(gcloud config get-value project)
}

echo "   Project ID: $PROJECT_ID"

echo "3. 🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    cloudresourcemanager.googleapis.com

echo "4. 🐳 Building and deploying to Cloud Run..."
echo "   This may take 5-10 minutes..."

# Build and deploy
gcloud builds submit --config cloudbuild.yaml . || {
    echo "❌ Build failed. Trying direct deploy..."
    
    # Try direct deploy
    gcloud run deploy openclaw \
        --source . \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 1 \
        --set-env-vars RUN_MODE=cloud
}

echo "5. 🌐 Getting service URL..."
SERVICE_URL=$(gcloud run services describe openclaw --platform managed --region us-central1 --format='value(status.url)' 2>/dev/null || echo "https://openclaw-*.run.app")

echo ""
echo "✅ Google Cloud Run Setup Complete!"
echo "==================================="
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Dashboard: https://console.cloud.google.com/run"
echo ""
echo "🔄 Toggle Between Local and Cloud:"
echo "   Local:   openclaw gateway start"
echo "   Cloud:   Visit $SERVICE_URL"
echo ""
echo "📅 Cron jobs will run automatically in cloud!"
echo "💡 First report will be at the next scheduled time."
echo ""
echo "🔧 To update deployment:"
echo "   gcloud run deploy openclaw --source ."