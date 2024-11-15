# Quick Deployment Guide for FAQ Generator

## Prerequisites
1. GitHub account
2. Railway.app account (https://railway.app)
3. OpenAI API key

## Deployment Steps

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. Deploy to Railway:

a. Go to Railway.app and sign in with GitHub
b. Click "New Project"
c. Choose "Deploy from GitHub repo"
d. Select your FAQ Generator repository
e. Click "Deploy Now"

3. Set Environment Variables:
- Go to your project settings in Railway
- Add the following variables:
  ```
  OPENAI_API_KEY=your_openai_api_key
  FLASK_ENV=production
  SECRET_KEY=your_secret_key
  ```

4. Your app will be automatically deployed! Railway will:
- Build the Docker container
- Install all dependencies
- Set up HTTPS
- Provide a public URL

## Monitoring
- View logs in Railway dashboard
- Monitor resource usage
- Check deployment status

## Updating
Just push changes to your GitHub repository:
```bash
git add .
git commit -m "Update description"
git push
```
Railway will automatically redeploy with your changes.

## Troubleshooting
1. If deployment fails:
   - Check Railway logs
   - Verify environment variables
   - Ensure all dependencies are in requirements.txt

2. If the app crashes:
   - Check resource limits
   - View application logs
   - Verify OpenAI API key

## Benefits of Railway Deployment
- Automatic HTTPS
- Easy scaling
- Built-in monitoring
- Automatic deployments
- No server configuration needed
- Free tier available
