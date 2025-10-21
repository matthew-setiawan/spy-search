# Render Deployment Guide for Spy Search

This guide will help you deploy Spy Search on Render using GPT-3.5-turbo.

## Prerequisites

- GitHub repository with your Spy Search code
- OpenAI API key
- Render account (free tier available)

## Step 1: Prepare Your Repository

1. **Ensure your `config.json` is configured for OpenAI:**
   ```json
   {
       "provider": "openai",
       "model": "gpt-3.5-turbo",
       "agents": ["reporter"],
       "db": "./local_files/test",
       "base_url": "https://api.openai.com/v1",
       "language": "en"
   }
   ```

2. **Create a `.env.example` file** (optional, for documentation):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Step 2: Deploy on Render

### Option A: Deploy as a Web Service (Recommended)

1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your spy-search repository

3. **Configure the Service**
   - **Name**: `spy-search` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave empty (uses root)
   - **Dockerfile Path**: `./Dockerfile`

4. **Set Environment Variables**
   Click "Advanced" and add these environment variables:
   
   **Required Variables:**
   ```
   OPENAI_API_KEY=your_actual_openai_api_key
   ```
   
   **Optional Variables:**
   ```
   PORT=8000
   HOST=0.0.0.0
   ```

5. **Configure Build Settings**
   - **Build Command**: Leave empty (Docker handles this)
   - **Start Command**: Leave empty (uses Dockerfile ENTRYPOINT)

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - This process takes 5-10 minutes

### Option B: Deploy as a Background Worker (Alternative)

If you prefer a worker setup:

1. **Create New Background Worker**
   - Click "New +" → "Background Worker"
   - Follow similar configuration as above
   - Use the same environment variables

## Step 3: Configure Custom Domain (Optional)

1. **In your Render service dashboard:**
   - Go to "Settings" → "Custom Domains"
   - Add your domain
   - Configure DNS as instructed

## Step 4: Monitor and Scale

1. **Monitor Logs**
   - Go to your service dashboard
   - Click "Logs" tab to view real-time logs
   - Check for any errors or issues

2. **Scale if Needed**
   - Free tier: 1 instance
   - Paid tiers: Scale up as needed
   - Auto-scaling available on paid plans

## Environment Variables Reference

### Required Variables:
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional Variables:
- `PORT`: Port number (default: 8000)
- `HOST`: Host binding (default: 0.0.0.0)
- `NODE_ENV`: Environment (production/development)

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check Dockerfile syntax
   - Ensure all dependencies are in requirements.txt
   - Verify frontend build process

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Verify API keys are valid
   - Check logs for specific error messages

3. **Memory Issues**
   - Render free tier has 512MB RAM limit
   - Consider upgrading to paid tier for production use

4. **Timeout Issues**
   - Free tier has 15-minute timeout
   - Consider upgrading for longer-running processes

### Debug Commands:

Check if your app works locally:
```bash
# Test locally with Docker
docker build -t spy-search .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key spy-search
```

## Cost Considerations

- **Free Tier**: 750 hours/month, 512MB RAM, 15-min timeout
- **Starter Plan**: $7/month, 512MB RAM, no timeout
- **Standard Plan**: $25/month, 1GB RAM, auto-scaling

## Security Notes

1. **Never commit API keys to your repository**
2. **Use Render's environment variables for secrets**
3. **Consider using Render's built-in SSL certificates**
4. **Regularly rotate your API keys**

## Next Steps

1. **Set up monitoring** with Render's built-in metrics
2. **Configure auto-deployments** from your main branch
3. **Set up health checks** for your endpoints
4. **Consider database integration** for production use

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Spy Search Issues: [GitHub Issues](https://github.com/JasonHonKL/spy-search/issues)
- Community Discord: [Discord Server](https://discord.gg/rrsMgBdJJt)
