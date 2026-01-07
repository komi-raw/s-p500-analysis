import os
import csv

def find_project_root(project_name="s-p500-analysis"):
    """
    Remonte les dossiers depuis l'emplacement du script
    jusqu'à trouver le dossier 's-p500-analysis'.
    """
    current = os.path.abspath(__file__)
    directory = os.path.dirname(current)

    while True:
        if project_name in os.listdir(directory):
            return os.path.join(directory, project_name)

        parent = os.path.dirname(directory)
        if parent == directory:
            raise FileNotFoundError(f"Dossier '{project_name}' introuvable.")
        directory = parent


def csv_to_sql():
    project_root = find_project_root()
    stocks_folder = os.path.join(project_root, "Stocks")

    if not os.path.exists(stocks_folder):
        stocks_folder = os.path.join(project_root, "stocks")
        if not os.path.exists(stocks_folder):
            raise FileNotFoundError("Le dossier 'Stocks' n'existe pas dans s-p500-analysis")

    # Dossier de sortie
    output_folder = os.path.join(project_root, "SQL_Output")
    os.makedirs(output_folder, exist_ok=True)
    sql_creat = "createTables.sql"
    sql_path_create = os.path.join(output_folder, sql_creat)
    with open(sql_path_create,"w",encoding="utf-8") as creat:
        creat.write("""CREATE TABLE company_data (
    companyIdx INT NOT NULL AUTO_INCREMENT,
    code    CHAR(10) NOT NULL,
    name    VARCHAR(100),
    PRIMARY KEY (companyIdx)
);
""")

    id = 0
    # Parcours des fichiers CSV
    for file in os.listdir(stocks_folder):
        if not file.lower().endswith(".csv"):
            continue

        csv_path = os.path.join(stocks_folder, file)
        sql_filename = file.replace(".csv", "")+"_price_dat.sql"
        sql_filename_2 = file.replace(".csv", "")
        sql_filename_2 += "_company_dat.sql"
        sql_path = os.path.join(output_folder, sql_filename)
        sql_path_2 = os.path.join(output_folder, sql_filename_2)

        id = id + 1

        with open(csv_path, newline='', encoding="utf-8") as csvfile, \
             open(sql_path, "w", encoding="utf-8") as sqlfile, \
             open(sql_path_2, "w", encoding="utf-8") as sqlfile2:

            reader = csv.DictReader(csvfile)

            sqlfile.write(f"""CREATE TABLE {file.replace(".csv", "")} (
    companyId INT NOT NULL,
    date    DATETIME NOT NULL,
    open    DECIMAL(10,4) NOT NULL,
    low     DECIMAL(10,4) NOT NULL,
    high    DECIMAL(10,4) NOT NULL,
    close   DECIMAL(10,4) NOT NULL,
    volume  BIGINT NOT NULL
);\n\n""")

            sqlfile.write(f"INSERT INTO {file.replace(".csv", "")} (companyId, date, open, low, high, close, volume)\nVALUES\n")
            sqlfile2.write("INSERT INTO company_data (companyIdx, code, name)\nVALUES\n")
            first = True
            
            line = (f"  ({id},'{file.replace(".csv", "")}', NULL)")

            sqlfile2.write(line)

            for row in reader:
                line = (
                    f"    ({id}, "
                    f"'{row['date']}', "
                    f"{row['open']}, "
                    f"{row['low']}, "
                    f"{row['high']}, "
                    f"{row['close']}, "
                    f"{row['volume']})"
                )

                if not first:
                    sqlfile.write(",\n")
                sqlfile.write(line)
                first = False

            sqlfile.write(";\n")

        print(f"➡ Fichier SQL généré : {sql_path}")


if __name__ == "__main__":
    csv_to_sql()
