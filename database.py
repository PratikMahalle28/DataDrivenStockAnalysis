# COMPLETE ONE-FILE DATABASE SETUP - Just update password and RUN!
# Save as: database_setup.py
# Run: python database_setup.py

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus

# 🚨 UPDATE ONLY THIS LINE WITH YOUR MySQL WORKBENCH PASSWORD 🚨
MYSQL_PASSWORD = ""  # ← PUT YOUR PASSWORD HERE (empty if no password)

# FIXED Connection (handles all 1045/2005 errors)
DB_CONFIG = {
    'user': 'root',
    'password': 'Pratik28@',
    'host': 'localhost',
    'port': '3306',
    'database': 'stock_analysis_db'
}

def setup_database():
    """Complete database setup in ONE function"""
    print("🚀 Starting COMPLETE database setup...")
    
    # URL-encode password (fixes @localhost error)
    encoded_password = quote_plus(DB_CONFIG['password'])
    
    # Connection strings
    test_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{encoded_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
    db_url = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{encoded_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    try:
        print("   🔍 Testing MySQL server connection...")
        
        # Step 1: Connect to MySQL server
        test_engine = create_engine(test_url, echo=False, pool_pre_ping=True)
        with test_engine.connect() as conn:
            # Create database
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`"))
            conn.commit()
            print("   ✅ Database created!")
        
        # Step 2: Connect to our database
        engine = create_engine(db_url, echo=False, pool_pre_ping=True)
        with engine.connect() as conn:
            # Create tables
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(10) UNIQUE NOT NULL,
                    company_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(10),
                    date DATE,
                    open_price DECIMAL(10,4),
                    high_price DECIMAL(10,4),
                    low_price DECIMAL(10,4),
                    close_price DECIMAL(10,4),
                    volume BIGINT,
                    FOREIGN KEY (symbol) REFERENCES stocks(symbol),
                    UNIQUE KEY unique_symbol_date (symbol, date)
                )
            """))
            
            # Test data
            conn.execute(text("INSERT IGNORE INTO stocks (symbol, company_name) VALUES ('AAPL', 'Apple Inc'), ('GOOGL', 'Google')"))
            conn.commit()
            
            version = conn.execute(text("SELECT VERSION()")).scalar()
            count = conn.execute(text("SELECT COUNT(*) FROM stocks")).scalar()
            
            print(f"✅ SUCCESS! MySQL v{version}")
            print(f"✅ Tables created with {count} test stocks")
            print("🎉 Database READY for stock analysis project!")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔧 QUICK FIX (2 minutes):")
        print("1. Open MySQL Workbench")
        print("2. Server → Startup/Shutdown → START MySQL")
        print("3. Copy password from Workbench connection")
        print("4. Paste in line 12: MYSQL_PASSWORD = 'your_password'")
        print("5. Run: ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';")
        print("6. python database_setup.py")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n📊 Your database is ready! Connect with:")
        print(f"engine = create_engine('{db_url}')")
