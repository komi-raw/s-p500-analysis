if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "Mac détecté → run en linux/amd64"
  docker run --platform linux/amd64 \
    -v ./SQL_Output/:/SQL \
    -d --name my_sp500_db \
    -p 3306:3306 \
    sp500_db
else
  docker run \
    -v ./SQL_Output/:/SQL \
    -d --name my_sp500_db \
    -p 3306:3306 \
    sp500_db
fi