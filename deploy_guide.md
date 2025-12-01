# 🚀 Deployment Guide

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone <your-repo-url>
   cd gov-data-crawler
   pip install -r requirements.txt
   ```

2. **Run Locally**
   ```bash
   streamlit run app.py
   ```

3. **Deploy to Streamlit Cloud**
   - Push code to GitHub repository
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set main file as `streamlit_app.py`
   - Deploy!

## GitHub Repository Setup

### 1. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Government Data Crawler"
```

### 2. Create GitHub Repository
1. Go to GitHub and create a new repository
2. Name it `gov-data-crawler`
3. Don't initialize with README (we already have one)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/gov-data-crawler.git
git branch -M main
git push -u origin main
```

## Streamlit Cloud Deployment

### 1. Connect to Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"

### 2. Configure Deployment
- **Repository**: YOUR_USERNAME/gov-data-crawler
- **Branch**: main
- **Main file path**: streamlit_app.py

### 3. Advanced Settings (Optional)
```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## Environment Variables (if needed)

For production deployment, you may need to set:

- `DATA_GOV_API_KEY` - For enhanced data.gov access
- `CENSUS_API_KEY` - For Census Bureau API access

## File Structure for Deployment

```
gov-data-crawler/
├── streamlit_app.py    # Entry point for Streamlit Cloud
├── app.py             # Main application
├── requirements.txt   # Dependencies
├── config.py         # Configuration
├── crawler/          # Web crawling modules
├── utils/            # Utility functions
├── data/             # Data storage (gitignored)
├── .gitignore        # Git ignore rules
└── README.md         # Project documentation
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are in requirements.txt
   - Check Python version compatibility (3.8+)

2. **Memory Issues**
   - Limit dataset size for free tier
   - Implement pagination for large results

3. **Rate Limiting**
   - Respect API rate limits
   - Implement caching to reduce requests

4. **Deployment Fails**
   - Check Streamlit logs in the cloud console
   - Verify all files are committed to GitHub
   - Ensure requirements.txt is complete

### Performance Tips

1. **Caching**
   - Use `@st.cache_data` for expensive operations
   - Cache API responses locally

2. **Memory Management**
   - Clear large datasets from session state when not needed
   - Use pagination for large datasets

3. **API Keys**
   - Store sensitive keys in Streamlit secrets
   - Use environment variables for configuration

## Next Steps After Deployment

1. **Monitor Usage**
   - Check Streamlit Cloud analytics
   - Monitor API rate limits

2. **Add Features**
   - More data sources
   - Advanced filtering
   - Data export formats
   - User authentication

3. **Optimize Performance**
   - Database integration
   - Async operations
   - Background data updates

## Support

- Streamlit Documentation: [docs.streamlit.io](https://docs.streamlit.io)
- Streamlit Community: [discuss.streamlit.io](https://discuss.streamlit.io)
- GitHub Issues: Create issues in your repository