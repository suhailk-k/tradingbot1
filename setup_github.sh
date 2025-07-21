#!/bin/bash
# GitHub Repository Setup Script
# Run this after creating the repository on GitHub.com

echo "🚀 Setting up GitHub repository connection..."

# Replace 'yourusername' with your actual GitHub username
read -p "Enter your GitHub username: " username

echo "📡 Adding GitHub remote..."
git remote add origin https://github.com/$username/tradingbot1.git

echo "⬆️ Pushing code to GitHub..."
git push -u origin main

echo "✅ Repository setup complete!"
echo "🌐 Your repository: https://github.com/$username/tradingbot1"
echo ""
echo "🚂 Ready for Railway deployment!"
echo "📋 Next steps:"
echo "1. Go to railway.app"
echo "2. Click 'New Project'"
echo "3. Select 'Deploy from GitHub repo'"
echo "4. Choose: $username/tradingbot1"
echo "5. Add environment variables"
echo "6. Deploy!"
