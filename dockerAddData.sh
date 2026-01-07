# ENTER DOCKER WITH THE FOLLOWING COMMAND #
docker exec -it my_sp500_db /bin/bash



mysql -u sp500_main -psp500_main sp500 < /SQL/createTables.sql

# ---- MYSQL IF SQL FILES GENERATED

rm -rf /SQL/createTables.sql

for file in /SQL/*_company_dat.sql; do mysql -u sp500_main -psp500_main sp500 < $file;done

for file in /SQL/*_price_dat.sql; do mysql -u sp500_main -psp500_main sp500 < $file;done

# ---- MYSQL IF CSV FILES GENERATED

mysqlimport --ignore-lines=1 --fields-terminated-by=, \
		-u root --password=sp500_root \
		sp500 /SQL/company_data.csv

mysqlimport --ignore-lines=1 --fields-terminated-by=, \
                -u root --password=sp500_root \
                sp500 /SQL/price_data.csv
