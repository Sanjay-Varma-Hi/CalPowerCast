# Frontend Deployment Guide

## 🚀 Quick Deploy to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy from the frontend directory:
```bash
cd frontend
vercel
```

3. Follow the prompts to complete the deployment.

### Option 2: Deploy via Vercel Dashboard

1. Push your code to GitHub:
```bash
cd ..
git add frontend/
git commit -m "Add Next.js frontend"
git push origin main
```

2. Go to [vercel.com](https://vercel.com) and sign in

3. Click "Add New Project"

4. Import your repository

5. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (set this in project settings if deploying from monorepo)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

6. Click "Deploy"

### Option 3: Deploy via GitHub Integration

1. Connect your GitHub account to Vercel
2. Select your repository
3. Vercel will auto-detect Next.js
4. Deploy!

## 🔧 Environment Variables

No environment variables needed for this deployment - the API endpoint is hardcoded in the frontend.

## 📝 Testing Locally

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000

## 🎯 Production URL

After deployment, you'll get a URL like:
```
https://calpowercast.vercel.app
```

## 🔄 Continuous Deployment

Once connected to GitHub, every push to `main` will automatically trigger a new deployment.

## 📊 Preview Deployments

Every pull request gets its own preview URL for testing.

## ⚡ Performance

- Automatic code splitting
- Image optimization
- Static page generation
- Edge functions support

## 🌐 Custom Domain

1. Go to your Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed
