# AgriBrain Deployment Guide

## Technology Stack

### Frontend
- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.4.0
- **Routing**: React Router DOM 6.26.0
- **UI Libraries**: 
  - Recharts (charts/data visualization)
  - Framer Motion (animations)
  - Lucide React (icons)
- **Package Manager**: npm

### Backend/ML
- **Language**: Python 3.x
- **ML Libraries**: scikit-learn, XGBoost, SHAP
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn

**Note**: The Python backend is for model training and analysis only. There is no live backend API server. The React frontend uses mock data stored in React Context.

---

## Project Structure

```
FinalYearProject/
├── frontend/
│   ├── react-app/          # Main React application
│   │   ├── src/
│   │   ├── dist/           # Production build output
│   │   ├── package.json
│   │   └── vite.config.js
│   ├── index.html          # Legacy static HTML frontend
│   └── styles.css
├── data/                    # ML datasets
├── models/                  # Trained ML models (.pkl files)
├── train_models.py          # ML model training script
├── shap_analysis.py         # SHAP explainability analysis
├── requirements.txt         # Python dependencies
├── vercel.json             # Vercel deployment config
└── DEPLOYMENT.md           # This file
```

---

## Environment Variables

The React app currently doesn't require any environment variables, as it uses local mock data.

If you add a backend API in the future, create a `.env` file based on `.env.example`:

```bash
cd frontend/react-app
cp .env.example .env
```

Then configure your API URL:
```
VITE_API_URL=https://your-api-domain.com/api
```

---

## Local Development

### Prerequisites
- Node.js 24.x or higher
- npm 12.x or higher
- Python 3.8+ (for ML scripts)

### Frontend Development

1. **Install dependencies**:
```bash
cd frontend/react-app
npm install
```

2. **Run development server**:
```bash
npm run dev
```
The app will open at `http://localhost:5173`

3. **Build for production**:
```bash
npm run build
```

4. **Preview production build**:
```bash
npm run preview
```

### Python ML Scripts (Optional)

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Train models**:
```bash
python train_models.py
```

3. **Generate SHAP analysis**:
```bash
python shap_analysis.py
```

---

## Production Deployment

### Deploy to Vercel (Recommended)

Vercel is the recommended platform for deploying the React frontend.

#### Method 1: Vercel CLI

1. **Install Vercel CLI**:
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy**:
```bash
# From the project root
vercel

# For production
vercel --prod
```

#### Method 2: GitHub Integration

1. **Push code to GitHub**:
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

2. **Connect to Vercel**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Configure Build Settings** (should be auto-configured):
   - **Build Command**: `cd frontend/react-app && npm install && npm run build`
   - **Output Directory**: `frontend/react-app/dist`
   - **Install Command**: `npm install`

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your application
   - You'll get a production URL like: `https://agribrain-dashboard.vercel.app`

### Custom Domain (Optional)

1. Go to your Vercel project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Follow Vercel's DNS configuration instructions

---

## Deployment Checklist

- [x] Dependencies installed and verified
- [x] Application runs locally without errors
- [x] Production build completes successfully
- [x] Production build previewed and tested
- [x] No secrets committed to repository
- [x] `.gitignore` configured properly
- [x] `.env.example` created for future API integration
- [x] Vercel configuration added
- [x] Vite config optimized for production
- [x] Routing configured for SPA

---

## Post-Deployment

### Verify Deployment

After deployment, test the following:

1. **Homepage loads**: Navigate to your deployed URL
2. **Routing works**: Test all routes (farms, crops, weather, analytics, etc.)
3. **Data displays**: Verify mock data appears correctly
4. **Responsive design**: Test on mobile, tablet, and desktop
5. **Performance**: Check Lighthouse scores

### Monitor Application

- **Vercel Analytics**: Enabled automatically for performance monitoring
- **Error Tracking**: Consider adding Sentry or similar for error tracking
- **Uptime Monitoring**: Consider adding a service like UptimeRobot

---

## Future Backend Integration

When you're ready to add a live backend API:

1. **Create Backend API** (suggestions):
   - FastAPI (Python) - recommended if integrating ML models
   - Node.js/Express
   - Django REST Framework

2. **Deploy Backend**:
   - Railway.app (Python/Node.js)
   - Render (Python/Node.js)
   - Heroku
   - AWS Lambda + API Gateway

3. **Update Frontend**:
   - Create API service files in `src/services/`
   - Replace mock data in `AppContext.jsx` with API calls
   - Add environment variables for API URL
   - Handle loading states and errors

4. **Configure CORS**:
   - Whitelist your Vercel frontend domain in backend CORS settings

---

## Troubleshooting

### Build Fails

**Issue**: Build command fails on Vercel

**Solution**:
```bash
# Test locally first
cd frontend/react-app
npm install
npm run build
```

Check for:
- Missing dependencies in `package.json`
- TypeScript/ESLint errors
- Import errors

### Routing Issues (404 on Refresh)

**Issue**: Routes return 404 when refreshing

**Solution**: Already configured in `vercel.json` with rewrites. Vercel will redirect all routes to `index.html` for client-side routing.

### Large Bundle Size

**Issue**: Application loads slowly

**Solution**:
- Already configured code splitting in `vite.config.js`
- Consider lazy loading routes:
```javascript
const Dashboard = lazy(() => import('./components/Dashboard'));
```

### Environment Variables Not Working

**Issue**: `import.meta.env` variables are undefined

**Solution**:
- Ensure variables are prefixed with `VITE_`
- Set them in Vercel Project Settings → Environment Variables
- Redeploy after adding variables

---

## Support

For issues or questions:
- Check Vercel logs: `vercel logs`
- Review build logs in Vercel dashboard
- Check browser console for frontend errors

---

## Summary

✅ **Frontend**: React app ready for deployment to Vercel
✅ **No Backend**: Application uses local mock data
✅ **ML Scripts**: Run locally for model training (not deployed)
✅ **Ready**: Application is production-ready

**Next Steps**:
1. Deploy to Vercel using the methods above
2. Test thoroughly
3. (Optional) Add custom domain
4. (Future) Integrate live backend API when needed

