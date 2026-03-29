#!/bin/bash
# ============================================================
#  S&P 500 Analysis Platform — First-time Setup (Docker/DB)
#  A lancer UNE SEULE FOIS avant le premier start.sh
# ============================================================
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER="my_sp500_db"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}  $*"; }
info() { echo -e "${BLUE}[--]${NC}  $*"; }
warn() { echo -e "${YELLOW}[!!]${NC}  $*"; }
fail() { echo -e "${RED}[ERR]${NC} $*"; exit 1; }

command -v docker &>/dev/null || fail "Docker introuvable."

# ---- Vérifier si déjà fait ------------------------------------------
if docker ps -a --filter "name=^${CONTAINER}$" --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER}$"; then
    warn "Le conteneur '$CONTAINER' existe déjà."
    read -rp "  Recréer et recharger les données ? (o/N) : " confirm
    if [[ "$confirm" != "o" && "$confirm" != "O" ]]; then
        info "Annulé."
        exit 0
    fi
    docker rm -f "$CONTAINER" > /dev/null
    ok "Ancien conteneur supprimé."
fi

# ---- Build ----------------------------------------------------------
info "Build de l'image Docker MySQL..."
cd "$ROOT_DIR"
bash dockerBuild.sh
ok "Image construite."

# ---- Run ------------------------------------------------------------
info "Création du conteneur..."
bash dockerRun.sh
ok "Conteneur démarré."

# ---- Attendre MySQL + utilisateur sp500_main ------------------------
info "Attente que MySQL et l'utilisateur sp500_main soient prêts..."
ready=0
for i in $(seq 1 40); do
    if docker exec "$CONTAINER" mysql -u sp500_main -psp500_main -e "SELECT 1;" sp500 &>/dev/null; then
        ready=1
        ok "MySQL prêt."
        break
    fi
    echo -n "."
    sleep 3
done
echo ""
[ $ready -eq 1 ] || fail "MySQL n'a pas démarré dans les temps."

# ---- Charger les données (pipe direct depuis l'hôte) ----------------
LOCAL_SQL="$ROOT_DIR/SQL_Output/SQL_Output_compiled/SQL_Output"
MYSQL_CMD="docker exec -i $CONTAINER mysql -u sp500_main -psp500_main sp500 2>/dev/null"

[ -f "$LOCAL_SQL/createTables.sql" ] || \
    fail "Fichiers SQL introuvables dans $LOCAL_SQL. Vérifie le dossier SQL_Output/SQL_Output_compiled/SQL_Output/"

info "Création des tables..."
$MYSQL_CMD < "$LOCAL_SQL/createTables.sql"
ok "Tables créées."

info "Chargement des données entreprises..."
for f in "$LOCAL_SQL"/*_company_dat.sql; do
    $MYSQL_CMD < "$f"
done
ok "Données entreprises chargées."

info "Chargement des données de prix (peut prendre plusieurs minutes)..."
for f in "$LOCAL_SQL"/*_price_dat.sql; do
    $MYSQL_CMD < "$f"
done
ok "Données de prix chargées."

# ---- Résumé ---------------------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup terminé !${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Tu peux maintenant lancer l'application : ${YELLOW}./start.sh${NC}"
echo ""
