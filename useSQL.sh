mysql -u sp500_main -psp500_main sp500 < /SQL/createTables.sql

rm -rf /SQL/createTables.sql

for file in /SQL/*_company_dat.sql; do mysql -u sp500_main -psp500_main sp500 < $file;done

for file in /SQL/*_price_dat.sql; do mysql -u sp500_main -psp500_main sp500 < $file;done
