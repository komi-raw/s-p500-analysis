#!/bin/bash
# ============================================================
#  S&P 500 Analysis Platform — Stop Script
# ============================================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/.pids"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}  $*"; }
warn() { echo -e "${YELLOW}[!!]${NC}  $*"; }

if [ ! -f "$PID_FILE" ]; then
    warn "Aucun fichier .pids trouvé — services peut-être déjà arrêtés."
    exit 0
fi

while IFS=' ' read -r name pid; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        ok "Arrêté : $name (PID $pid)"
    else
        warn "Déjà arrêté ou introuvable : $name (PID $pid)"
    fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo ""
ok "Tous les services arrêtés."
echo ""
echo "  Pour arrêter MySQL (Docker) :"
echo "    docker stop my_sp500_db"
echo ""
