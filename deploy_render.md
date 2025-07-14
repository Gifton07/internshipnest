# Deploy Insurance Prediction App to Render

## Prerequisites
- A Render account (free tier available)
- Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

Make sure your repository has these files:
- `app.py` (your Flask application)
- `requirements_basic.txt` (dependencies)
- `insurance.csv` (your dataset)
- `templates/index.html` (your UI template)

## Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub/GitLab account
3. Verify your email address

## Step 3: Deploy Your App

### Option A: Deploy via Render Dashboard

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the repository containing your insurance app

2. **Configure the Service**
   - **Name**: `insurance-prediction-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_basic.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (or choose paid for better performance)

3. **Environment Variables** (Optional)
   - Add any environment variables if needed
   - For now, you can leave this empty

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Option B: Deploy via Render CLI

1. Install Render CLI:
   ```bash
   npm install -g @render/cli
   ```

2. Login to Render:
   ```bash
   render login
   ```

3. Deploy your app:
   ```bash
   render deploy
   ```

## Step 4: Configure Your App for Render

Your `app.py` should already be configured correctly, but make sure it uses the PORT environment variable:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

## Step 5: Monitor Your Deployment

1. **Check Build Logs**
   - Go to your service dashboard
   - Click on "Logs" to see build and runtime logs
   - Monitor for any errors during deployment

2. **Test Your App**
   - Once deployed, visit your app URL
   - Test the prediction functionality
   - Check if the model loads correctly

## Step 6: Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain name
   - Configure DNS records as instructed

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check if all dependencies are in `requirements_basic.txt`
   - Ensure `insurance.csv` is in your repository
   - Verify Python version compatibility

2. **Runtime Errors**
   - Check application logs in Render dashboard
   - Ensure model files are being created/loaded correctly
   - Verify file paths are correct

3. **Memory Issues**
   - Free tier has 512MB RAM limit
   - Consider upgrading to paid plan for larger datasets
   - Optimize your model if needed

### Performance Optimization:

1. **Upgrade Plan**
   - Free tier: 512MB RAM, shared CPU
   - Starter: 1GB RAM, shared CPU ($7/month)
   - Standard: 2GB RAM, dedicated CPU ($25/month)

2. **Caching**
   - Consider adding Redis for caching predictions
   - Implement model result caching

3. **Database Integration**
   - Add PostgreSQL for storing predictions
   - Use Render's managed database service

## Environment Variables

You can add these environment variables in Render dashboard:

```
FLASK_ENV=production
FLASK_DEBUG=False
USD_TO_INR_RATE=83.0
```

## Monitoring and Logs

- **Application Logs**: Available in Render dashboard
- **Build Logs**: Shows dependency installation and build process
- **Health Checks**: Render automatically monitors your app
- **Metrics**: Basic metrics available in dashboard

## Scaling

- **Auto-scaling**: Available on paid plans
- **Manual scaling**: Adjust instance count as needed
- **Load balancing**: Automatic on multiple instances

## Security

- **HTTPS**: Automatically enabled
- **Environment variables**: Securely stored
- **Access control**: Configure as needed

## Cost Optimization

- **Free tier**: 750 hours/month
- **Sleep mode**: Free tier apps sleep after 15 minutes of inactivity
- **Paid plans**: Start at $7/month for always-on service

## Next Steps

1. **Set up monitoring**: Add logging and error tracking
2. **Add database**: Store prediction history
3. **Implement caching**: Improve response times
4. **Add authentication**: Secure your API endpoints
5. **Set up CI/CD**: Automatic deployments on code changes

Your app should now be live on Render! The URL will be something like:
`https://your-app-name.onrender.com` 