# 🚀 Deploy to Vercel - Step by Step Guide

## Why Vercel?
- **Excellent performance** and global CDN
- **Free tier** with generous limits
- **Automatic deployments** from GitHub
- **Great for frontend-heavy apps**

## Step 1: Prepare for Vercel

1. **Create `vercel.json`**:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

2. **Update `requirements.txt`**:
   ```
   Flask==2.3.3
   pandas==2.0.3
   numpy==1.24.3
   scikit-learn==1.3.0
   gunicorn==21.2.0
   ```

## Step 2: Deploy to Vercel

### Option A: Using Vercel Dashboard

1. **Go to Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Sign up/Login with GitHub

2. **Import Project**:
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Python

3. **Configure**:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `.`
   - Install Command: `pip install -r requirements.txt`

4. **Environment Variables**:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete

### Option B: Using Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Follow prompts**:
   - Link to existing project or create new
   - Confirm settings
   - Deploy

## Step 3: Verify Deployment

Your app will be at: `https://your-app-name.vercel.app`

Test endpoints:
```bash
# Health check
curl https://your-app-name.vercel.app/health

# Prediction
curl -X POST https://your-app-name.vercel.app/predict \
  -H "Content-Type: application/json" \
  -d '{"age": 25, "sex": "male", "bmi": 28.5, "children": 2, "smoker": "no", "region": "southwest"}'
```

## Vercel Limitations

- **Serverless functions** have execution time limits
- **Cold starts** for ML models
- **Memory limits** for large models
- **Not ideal** for heavy ML workloads

## Custom Domain

1. **Add Domain**:
   - Go to project → "Settings" → "Domains"
   - Add your domain

2. **Configure DNS**:
   - Point to Vercel's servers
   - Automatic SSL certificate

## Performance

- **Global CDN** for static assets
- **Edge functions** for better performance
- **Automatic scaling**

## Cost

- **Hobby**: Free (unlimited deployments)
- **Pro**: $20/month (team features)
- **Enterprise**: Custom pricing

## Best Practices for Vercel

1. **Optimize model size** for serverless
2. **Use edge caching** for predictions
3. **Consider model serving** separately
4. **Monitor function execution times** 