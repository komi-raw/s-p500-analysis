#!/bin/bash
# ============================================================
#  S&P 500 Analysis Platform — Install & Launch Script
# ============================================================
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT_DIR/venv"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/.pids"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC}  $*"; }
info() { echo -e "${BLUE}[--]${NC}  $*"; }
warn() { echo -e "${YELLOW}[!!]${NC}  $*"; }
fail() { echo -e "${RED}[ERR]${NC} $*"; exit 1; }

# ---- GROQ_API_KEY ---------------------------------------------------
if [ -z "$GROQ_API_KEY" ]; then
    echo ""
    warn "GROQ_API_KEY n'est pas définie."
    read -rp "  Entrez votre clé Groq (laisser vide pour ignorer le service IA) : " GROQ_API_KEY
    echo ""
fi
if [ -z "$GROQ_API_KEY" ]; then
    warn "Le service sp500_ia (LLM) sera démarré SANS clé Groq — les appels IA échoueront."
fi

# ---- Prérequis -------------------------------------------------------
info "Vérification des prérequis..."

# Python — vérifie que ce n'est pas le stub Windows Store (qui ne fait rien sous WSL)
check_python() {
    # Le stub Windows Store existe en tant que commande mais retourne une erreur à l'exécution
    if ! command -v python3 &>/dev/null; then
        return 1
    fi
    # Tester une exécution réelle
    if ! python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
        return 1
    fi
    return 0
}

if ! check_python; then
    warn "Python 3 absent ou non fonctionnel — installation via apt..."
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv
    check_python || fail "Impossible d'installer Python 3. Installez-le manuellement : sudo apt install python3 python3-venv"
fi

ok "Python  $(python3 --version)"

command -v node    &>/dev/null || fail "Node.js introuvable. Installez-le : https://nodejs.org"
command -v npm     &>/dev/null || fail "npm introuvable."
command -v docker  &>/dev/null || fail "Docker introuvable. Installez Docker Desktop : https://www.docker.com/products/docker-desktop"

ok "Node.js $(node --version)"
ok "npm     $(npm --version)"
ok "Docker  $(docker --version | awk '{print $3}')"

# ---- Arrêter les services existants si déjà lancés ------------------
if [ -f "$PID_FILE" ]; then
    warn "Des services sont peut-être déjà en cours. Arrêt préalable..."
    "$ROOT_DIR/stop.sh" 2>/dev/null || true
fi

mkdir -p "$LOG_DIR"
> "$PID_FILE"

# ---- MySQL Docker ----------------------------------------------------
info "Démarrage de MySQL (Docker)..."

CONTAINER="my_sp500_db"

if docker ps --filter "name=^${CONTAINER}$" --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    ok "Conteneur MySQL déjà en cours d'exécution."
else
    if docker ps -a --filter "name=^${CONTAINER}$" --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        info "Redémarrage du conteneur existant..."
        docker start "$CONTAINER"
        ok "MySQL redémarré."
    else
        info "Première installation — build + run de MySQL..."
        cd "$ROOT_DIR"
        bash dockerBuild.sh
        bash dockerRun.sh
        ok "MySQL créé et démarré."

        info "Chargement des données SQL (peut prendre quelques minutes)..."
        # Attendre que MySQL soit prêt
        for i in $(seq 1 30); do
            if docker exec "$CONTAINER" mysqladmin ping -u sp500_main -psp500_main --silent 2>/dev/null; then
                ok "MySQL prêt."
                break
            fi
            echo -n "."
            sleep 2
        done
        bash dockerAddData.sh
        ok "Données chargées."
    fi
fi

# ---- Environnement Python (venv) ------------------------------------
info "Configuration de l'environnement Python..."

if [ ! -f "$VENV/bin/activate" ]; then
    info "Création du venv..."
    python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"

info "Installation des dépendances Python..."
pip install --quiet --upgrade pip
pip install --quiet fastapi "uvicorn[standard]" sqlalchemy pymysql groq requests numpy scikit-learn
# torch et transformers sont lourds — installer seulement si absents
python3 -c "import torch" 2>/dev/null        || pip install torch
python3 -c "import transformers" 2>/dev/null || pip install transformers

ok "Dépendances Python OK."

# ---- Frontend (npm) --------------------------------------------------
info "Installation des dépendances frontend (npm)..."
cd "$ROOT_DIR/sp500_front"
npm install --silent
ok "npm install OK."

# ---- Lancement des services ------------------------------------------
cd "$ROOT_DIR"
source "$VENV/bin/activate"

start_service() {
    local name=$1
    local dir=$2
    local cmd=$3
    local port=$4
    local log="$LOG_DIR/${name}.log"

    info "Démarrage de $name (port $port)..."
    cd "$ROOT_DIR/$dir"
    eval "GROQ_API_KEY='$GROQ_API_KEY' $cmd" > "$log" 2>&1 &
    local pid=$!
    echo "$name $pid" >> "$PID_FILE"
    cd "$ROOT_DIR"

    # Attendre que le port soit ouvert (max 15s)
    for i in $(seq 1 15); do
        sleep 1
        if curl -s "http://localhost:$port" &>/dev/null || \
           curl -s "http://localhost:$port/health" &>/dev/null || \
           curl -s "http://localhost:$port/docs" &>/dev/null; then
            ok "$name démarré  →  http://localhost:$port   (PID $pid)"
            return
        fi
    done
    # Le service a peut-être pris plus de temps — on affiche juste un avertissement
    warn "$name PID $pid — pas encore de réponse HTTP sur le port $port (vérifier $log)"
}

start_service "sp500_back" "sp500_back" \
    "$VENV/bin/uvicorn main:app --port 8000" 8000

start_service "sp500_ml" "sp500_ml" \
    "$VENV/bin/uvicorn main:app --port 8002" 8002

start_service "sp500_ia" "sp500_ia" \
    "$VENV/bin/uvicorn main:app --port 8001" 8001

# Frontend en dernier
info "Démarrage du frontend Vue (port 5173)..."
cd "$ROOT_DIR/sp500_front"
npm run dev -- --host > "$LOG_DIR/sp500_front.log" 2>&1 &
FRONT_PID=$!
echo "sp500_front $FRONT_PID" >> "$PID_FILE"
cd "$ROOT_DIR"

# Attendre Vite
for i in $(seq 1 20); do
    sleep 1
    if curl -s "http://localhost:5173" &>/dev/null; then
        ok "sp500_front démarré  →  http://localhost:5173   (PID $FRONT_PID)"
        break
    fi
done

# ---- Résumé ----------------------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Tous les services sont lancés !${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Frontend    →  ${BLUE}http://localhost:5173${NC}"
echo -e "  API Back    →  ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  Service IA  →  ${BLUE}http://localhost:8001/docs${NC}"
echo -e "  Service ML  →  ${BLUE}http://localhost:8002/docs${NC}"
echo ""
echo -e "  Logs        →  ${YELLOW}$LOG_DIR/${NC}"
echo -e "  Arrêt       →  ${YELLOW}./stop.sh${NC}"
echo ""
