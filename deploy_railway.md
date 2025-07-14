# 🚀 Deploy to Railway - Step by Step Guide

## Prerequisites
- GitHub account
- Railway account (free at railway.app)

## Step 1: Prepare Your Code

1. **Install Railway CLI** (optional but recommended):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

## Step 2: Deploy to Railway

### Option A: Using Railway Dashboard (Easiest)

1. **Go to Railway Dashboard**:
   - Visit [railway.app](https://railway.app)
   - Sign up/Login with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository

3. **Configure Environment**:
   - Railway will automatically detect it's a Python app
   - Add environment variables if needed:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-secret-key-here
     ```

4. **Deploy**:
   - Railway will automatically build and deploy
   - You'll get a URL like: `https://your-app-name.railway.app`

### Option B: Using Railway CLI

1. **Initialize Railway Project**:
   ```bash
   railway init
   ```

2. **Deploy**:
   ```bash
   railway up
   ```

3. **Get your URL**:
   ```bash
   railway domain
   ```

## Step 3: Verify Deployment

1. **Check Health**:
   ```bash
   curl https://your-app-name.railway.app/health
   ```

2. **Test Prediction**:
   ```bash
   curl -X POST https://your-app-name.railway.app/predict \
     -H "Content-Type: application/json" \
     -d '{
       "age": 25,
       "sex": "male",
       "bmi": 28.5,
       "children": 2,
       "smoker": "no",
       "region": "southwest"
     }'
   ```

## Step 4: Custom Domain (Optional)

1. **Add Custom Domain**:
   - Go to your project in Railway dashboard
   - Click "Settings" → "Domains"
   - Add your custom domain

2. **Configure DNS**:
   - Point your domain to Railway's servers
   - Wait for DNS propagation

## Environment Variables

Add these in Railway dashboard under "Variables":

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
USD_TO_INR_RATE=83.0
```

## Monitoring

Railway provides:
- **Logs**: View real-time logs in dashboard
- **Metrics**: CPU, memory usage
- **Deployments**: Automatic deployments on git push

## Scaling

- **Free Tier**: 500 hours/month
- **Pro Plan**: $5/month for unlimited usage
- **Team Plan**: $20/month for team features

## Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check `requirements.txt` has all dependencies
   - Ensure `app.py` is in root directory

2. **App Crashes**:
   - Check logs in Railway dashboard
   - Verify environment variables are set

3. **Model Not Loading**:
   - Ensure `insurance.csv` is in repository
   - Check if model files are generated

### Useful Commands:

```bash
# View logs
railway logs

# Restart app
railway service restart

# Check status
railway status
```

## Next Steps

1. **Set up monitoring** with Railway's built-in tools
2. **Configure automatic deployments** from GitHub
3. **Add custom domain** for professional look
4. **Set up alerts** for downtime

Your app will be live at: `https://your-app-name.railway.app` 🎉 