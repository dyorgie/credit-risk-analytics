import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, exc

print("File is being read!") # Add this line

def main():
    # Load Credentials
    load_dotenv()
    
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    # Create the SQLAlchemy connection string
    connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)

    print("Starting ETL pipeline...")

    try:
        
        # EXTRACT: Read the raw CSV
        
        csv_path = os.path.join("data", "raw", "UCI_Credit_Card.csv")
        print(f"Extracting data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        
        # TRANSFORM: Clean up for SQL
        
        print("Transforming data...")
        
       
        # Periods in column names cause syntax errors in SQL, so we replace them.
        df.columns = [col.replace('.', '_').lower() for col in df.columns]
        
        
        # LOAD: Push to MySQL
        
        print("Loading data into MySQL database...")
        table_name = "customer_risk_profiles"
        
        # 'replace' drops the table if it exists and creates a new one. 
        # 'append' would add to it. For initial ingestion, replace is safest.
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
        
        print(f"Success! {len(df)} rows successfully loaded into the '{table_name}' table.")

    except exc.SQLAlchemyError as e:
        print(f"Database Error: {e}")
    except FileNotFoundError:
        print("Error: Could not find the CSV file. Ensure it is at data/raw/credit_card_data.csv")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()