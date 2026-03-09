from pathlib import Path
import shutil

# Configuration
CSV_FILENAME = "01_import_sp500.csv"
CSV_CONTAINER_PATH = "/SQL/01_import_sp500.csv"
OUTPUT_DIR = Path("SQL_Output")
OUTPUT_SQL_FILE = OUTPUT_DIR / "01_import_sp500.sql"
TABLE_NAME = "sp500_company_data"

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = Path("memo/SP500_Constituent.csv")
    destination = Path("SQL_Output/01_import_sp500.csv")
    shutil.copy(source, destination)
    sql = f"""
USE sp500;

DROP TABLE IF EXISTS {TABLE_NAME};

CREATE TABLE {TABLE_NAME} (
    symbol VARCHAR(10) NOT NULL,
    security VARCHAR(255) NOT NULL,
    gics_sector VARCHAR(100) NOT NULL,
    gics_sub_industry VARCHAR(150) NOT NULL,
    headquarters_location VARCHAR(255) NOT NULL,
    date_added DATE NULL,
    cik CHAR(10) NOT NULL,
    founded VARCHAR(50) NULL,
    PRIMARY KEY (symbol)
);

LOAD DATA INFILE '{CSV_CONTAINER_PATH}'
INTO TABLE {TABLE_NAME}
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS
(
    symbol,
    security,
    gics_sector,
    gics_sub_industry,
    headquarters_location,
    @date_added,
    cik,
    founded
)
SET date_added = NULLIF(@date_added, '');
""".strip()

    with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as f:
        f.write(sql)

    print(f"✔ Fichier SQL généré : {OUTPUT_SQL_FILE}")

if __name__ == "__main__":
    main()
    print(f"Run the following command: docker exec -it my_sp500_db /bin/bash")
    print(f"And then : mysql -u root -psp500_root sp500 < /SQL/01_import_sp500.sql")
