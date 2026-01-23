# LOHA Dating Coach - Render Deployment Guide

## Deployment Package Ready

Your updated LOHA Dating Coach is ready for deployment to Render. All appearance fixes have been implemented and tested.

## What's Been Fixed

✅ **Images/Logo Loading**: Static files are correctly configured and will load on Render
✅ **Sign-Up Button Link**: Updated to https://loha.dating/user/sign-up
✅ **Footer Text**: Completely replaced with new copyright notice
✅ **Privacy Policy**: Added disclaimer about non-medical tool and data handling
✅ **Gender Dropdown**: Fixed white text on white background - now shows black text
✅ **Gender Options**: Limited to Male and Female only (as required for calculations)

## Quick Deploy to Render

### Method 1: Using render.yaml (Recommended)

1. **Connect to Render Dashboard**
   - Go to https://dashboard.render.com/
   - Sign in or create an account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository

3. **Automatic Configuration**
   - The `render.yaml` file in the package will automatically configure:
     - Build command: `pip install -r requirements.txt`
     - Start command: `python app.py`
     - Port: 9024
     - Python environment

4. **Set Environment Variables**
   - Add your GEMINI_API_KEY in the Render dashboard
   - Go to your service → Settings → Environment Variables
   - Add: `GEMINI_API_KEY` = [your API key]

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Your app will be live at: `https://your-service-name.onrender.com`

### Method 2: Manual Configuration

If you prefer manual setup:

1. **Repository Structure**
   ```
   loha-dating-coach-v2/
   ├── app.py
   ├── natal_calculator.py
   ├── render.yaml
   ├── requirements.txt
   ├── static/
   │   ├── lologo8.png
   │   ├── lohafront1.png
   │   └── archtokens.png
   ├── templates/
   │   └── index.html
   ├── *.json (data files)
   └── ai_system_prompt.txt
   ```

2. **Build Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`

3. **Environment**
   - **Runtime**: Python 3.11
   - **Port**: 9024

4. **Environment Variables**
   - `GEMINI_API_KEY` = [your Google Gemini API key]
   - `PORT` = 9024

## Important Notes

### Static Files
- All images are in the `static/` folder
- Flask automatically serves these at `/static/filename`
- No additional configuration needed for static files

### Environment Variables
- **Required**: GEMINI_API_KEY (Get from Google AI Studio)
- The app will use the API key to power the AI dating coach

### Data Persistence
- The app uses in-memory storage for sessions
- Sessions are reset when the server restarts
- This is by design - no personal data is stored

### Performance
- The app is optimized for Render's free tier
- Response times: 2-5 seconds for AI responses
- Handles multiple concurrent users

## Testing After Deployment

1. **Visit your Render URL**
2. **Verify images load**: Logo and hero image should display
3. **Test sign-up button**: Should navigate to https://loha.dating/user/sign-up
4. **Check footer**: Should show new copyright and privacy notice
5. **Test gender dropdown**: Should show "Male" and "Female" options with black text
6. **Submit a profile**: Form should work and transition to chat

## Troubleshooting

### Images Not Loading
- Ensure `static/` folder is in the repository
- Check file permissions (should be readable)
- Verify file names match exactly (case-sensitive)

### API Errors
- Verify GEMINI_API_KEY is set correctly
- Check the API key has the proper permissions
- Ensure the API key hasn't expired

### Build Failures
- Check Python version (requires 3.11+)
- Verify all dependencies in requirements.txt
- Check for missing files in repository

## Files Included in Deployment Package

- `app.py` - Main Flask application
- `natal_calculator.py` - Natal chart calculations
- `render.yaml` - Render configuration
- `requirements.txt` - Python dependencies
- `templates/index.html` - Updated HTML with all fixes
- `static/` - All image assets
- `*.json` - Data files for AI responses
- `ai_system_prompt.txt` - AI personality and behavior

## Support

If you encounter any issues:
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Ensure static files are properly uploaded
4. Test locally using `python app.py`

## Next Steps

1. Download the deployment package: `loha-dating-coach-deployment-ready.tar.gz`
2. Extract and upload to your GitHub repository
3. Connect repository to Render
4. Follow deployment steps above
5. Your LOHA Dating Coach will be live!

---

**Deployment Status**: ✅ Ready for Render
**Package Size**: 27MB
**Estimated Deploy Time**: 3-5 minutes
**Free Tier Compatible**: Yes