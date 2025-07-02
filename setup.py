#!/usr/bin/env python3
"""
Setup script for AI Stock Advisor
This script helps set up the project environment and dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def install_dependencies():
    """Install all required Python packages"""
    packages = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0", 
        "numpy>=1.24.0",
        "yfinance>=0.2.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "trafilatura>=1.6.0",
        "nltk>=3.8.0",
        "spacy>=3.7.0",
        "plotly>=5.15.0",
        "python-dateutil>=2.8.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}"):
            return False
    
    return True

def setup_spacy():
    """Download the required spaCy model"""
    return run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model")

def setup_nltk():
    """Download required NLTK data"""
    try:
        print("📦 Setting up NLTK data...")
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data setup completed")
        return True
    except Exception as e:
        print(f"❌ NLTK setup failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("🔑 Checking environment variables...")
    
    if not os.getenv('NEWS_API_KEY'):
        print("⚠️  NEWS_API_KEY not found in environment variables")
        print("   Get your free API key from: https://newsapi.org")
        print("   Then set it with: export NEWS_API_KEY='your_key_here'")
        return False
    else:
        print("✅ NEWS_API_KEY found")
        return True

def main():
    """Main setup function"""
    print("🤖 AI Stock Advisor Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup spaCy
    if not setup_spacy():
        print("❌ Failed to setup spaCy")
        sys.exit(1)
    
    # Setup NLTK
    if not setup_nltk():
        print("❌ Failed to setup NLTK")
        sys.exit(1)
    
    # Check environment
    env_ok = check_environment()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    
    if not env_ok:
        print("\n⚠️  Don't forget to set your NEWS_API_KEY before running the app")
    
    print("\n🚀 To start the application:")
    print("   streamlit run app.py --server.port 5000")
    print("\n📖 For more information, check the README.md file")

if __name__ == "__main__":
    main()