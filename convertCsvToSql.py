import os
import csv

def find_project_root(project_name="projetMegaDonne"):
    """
    Remonte les dossiers depuis l'emplacement du script
    jusqu'à trouver le dossier 'projetMegaDonne'.
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
        raise FileNotFoundError("Le dossier 'Stocks' n'existe pas dans projetMegaDonne")

    # Dossier de sortie
    output_folder = os.path.join(project_root, "SQL_Output")
    os.makedirs(output_folder, exist_ok=True)

    # Parcours des fichiers CSV
    for file in os.listdir(stocks_folder):
        if not file.lower().endswith(".csv"):
            continue

        csv_path = os.path.join(stocks_folder, file)
        sql_filename = file.replace(".csv", ".sql")
        sql_path = os.path.join(output_folder, sql_filename)

        with open(csv_path, newline='', encoding="utf-8") as csvfile, \
             open(sql_path, "w", encoding="utf-8") as sqlfile:

            reader = csv.DictReader(csvfile)

            sqlfile.write("INSERT INTO price_data (file_name, date, open, low, high, close, volume)\nVALUES\n")

            first = True

            for row in reader:
                line = (
                    f"    ('{file}', "
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
