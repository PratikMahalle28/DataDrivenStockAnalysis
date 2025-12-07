# run.py - Complete project setup
import subprocess
import os
import sys
from pathlib import Path

def setup_project():
    """Complete project setup"""
    print("🚀 Stock Performance Dashboard - Complete Setup")
    print("=" * 60)
    
    # 1. Create folder structure
    Path("data/csv").mkdir(exist_ok=True, parents=True)
    Path("data/yaml").mkdir(exist_ok=True, parents=True)
    
    # 2. Create database
    print("\n1️⃣ Creating SQL Database...")
    subprocess.run([sys.executable, "database.py"], check=True)
    
    # 3. Test Streamlit
    print("\n2️⃣ Starting Streamlit Dashboard...")
    print("🌐 Open: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

if __name__ == "__main__":
    setup_project()
