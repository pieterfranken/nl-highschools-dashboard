# 🚀 Streamlit Community Cloud Deployment Guide

This guide will help you deploy the Dutch High Schools Dashboard to Streamlit Community Cloud for free public access.

## Prerequisites

1. **GitHub Account**: You'll need a GitHub account to host the code
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## Step-by-Step Deployment

### 1. 📁 Prepare Your Repository

1. **Create a new GitHub repository:**
   - Go to [github.com](https://github.com) and create a new repository
   - Name it something like `nl-highschools-dashboard`
   - Make it public (required for free Streamlit Cloud)

2. **Upload your files:**
   Upload these essential files to your repository:
   ```
   ├── app.py                              # Main dashboard application
   ├── nl_highschools_full.csv            # Processed dataset
   ├── requirements.txt                    # Python dependencies
   ├── .streamlit/config.toml             # Streamlit configuration
   ├── README.md                          # Documentation
   └── .gitignore                         # Git ignore file
   ```

### 2. 🌐 Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App:**
   - Click "New app"
   - Select your repository: `your-username/nl-highschools-dashboard`
   - Set main file path: `app.py`
   - Choose a custom URL (optional): `your-app-name.streamlit.app`

3. **Deploy:**
   - Click "Deploy!"
   - Wait for the deployment to complete (usually 2-5 minutes)

### 3. ✅ Verify Deployment

Your app will be available at:
```
https://your-app-name.streamlit.app
```

## 📋 Deployment Checklist

- [ ] GitHub repository created and public
- [ ] All required files uploaded to repository
- [ ] `requirements.txt` includes all dependencies
- [ ] `app.py` is in the root directory
- [ ] Dataset file `nl_highschools_full.csv` is included
- [ ] Streamlit Cloud app created and deployed
- [ ] App URL is accessible and working

## 🔧 Troubleshooting

### Common Issues:

1. **"Module not found" errors:**
   - Check that all dependencies are listed in `requirements.txt`
   - Ensure version constraints are compatible

2. **"File not found" errors:**
   - Verify `nl_highschools_full.csv` is in the repository
   - Check file paths are relative to the app root

3. **Memory issues:**
   - The dataset is optimized for cloud deployment
   - If issues persist, consider data sampling for demo purposes

4. **Slow loading:**
   - Data is cached using `@st.cache_data`
   - First load may be slower, subsequent loads will be faster

### Performance Tips:

- **Data Caching**: The app uses Streamlit's caching for optimal performance
- **Memory Optimization**: String columns are optimized for memory usage
- **Responsive Design**: Works well on both desktop and mobile

## 🔄 Updating Your Deployment

To update your deployed app:

1. **Push changes to GitHub:**
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push origin main
   ```

2. **Automatic redeployment:**
   - Streamlit Cloud automatically redeploys when you push to GitHub
   - Changes typically appear within 1-2 minutes

## 📊 Monitoring Usage

Streamlit Cloud provides:
- **Usage analytics** in your dashboard
- **Error logs** for debugging
- **Performance metrics** for optimization

## 🎯 Next Steps

After successful deployment:

1. **Share your dashboard** with colleagues and stakeholders
2. **Monitor usage** and gather feedback
3. **Iterate and improve** based on user needs
4. **Consider custom domain** for professional use

## 📞 Support

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: For project-specific issues

---

🎉 **Congratulations!** Your Dutch High Schools Dashboard is now live and accessible to anyone with the URL!
