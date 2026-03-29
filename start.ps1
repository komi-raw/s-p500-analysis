# ============================================================
#  S&P 500 Analysis Platform — Launch Script (Windows)
# ============================================================

$ErrorActionPreference = "Stop"
$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV     = "$ROOT_DIR\venv"
$LOG_DIR  = "$ROOT_DIR\logs"
$PID_FILE = "$ROOT_DIR\.pids"

function ok   { param($msg) Write-Host "[OK]  $msg" -ForegroundColor Green  }
function info { param($msg) Write-Host "[--]  $msg" -ForegroundColor Cyan   }
function warn { param($msg) Write-Host "[!!]  $msg" -ForegroundColor Yellow }
function fail { param($msg) Write-Host "[ERR] $msg" -ForegroundColor Red; exit 1 }

# ---- GROQ_API_KEY ---------------------------------------------------
if (-not $env:GROQ_API_KEY) {
    Write-Host ""
    warn "GROQ_API_KEY n'est pas definie."
    $env:GROQ_API_KEY = Read-Host "  Entrez votre cle Groq (laisser vide pour ignorer le service IA)"
    Write-Host ""
}
if (-not $env:GROQ_API_KEY) {
    warn "Le service sp500_ia (LLM) sera demarre SANS cle Groq -- les appels IA echoueront."
}

# ---- Python ----------------------------------------------------------
info "Verification de Python..."

function Find-Python {
    foreach ($cmd in @("python", "python3")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if (-not $found) { continue }
        # Rejeter le stub Windows Store
        if ($found.Source -like "*WindowsApps*") { continue }
        # Verifier execution reelle
        $ver = & $found.Source --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "Python 3\.\d+") {
            return $found.Source
        }
    }
    return $null
}

$PYTHON = Find-Python
if (-not $PYTHON) {
    fail @"
Python 3 est absent, trop vieux, ou pointe vers le stub Windows Store.

  Solutions :
  1. Telecharger Python depuis  https://www.python.org/downloads/
     -> Cocher "Add Python to PATH" lors de l'installation
  2. Ou via winget :  winget install Python.Python.3.12
  3. Desactiver le stub Windows Store :
     Parametres -> Applications -> Alias d'execution d'application
     -> Desactiver "python.exe" et "python3.exe"

Relancez le script apres installation.
"@
}

ok "Python  $(& $PYTHON --version)"

# ---- Node / npm -----------------------------------------------------
info "Verification de Node.js et npm..."

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    fail "Node.js introuvable.`n  Telecharger : https://nodejs.org  (choisir LTS)"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    fail "npm introuvable (normalement installe avec Node.js)."
}

ok "Node.js $(node --version)"
ok "npm     $(npm --version)"

# ---- Arreter les services existants ---------------------------------
if (Test-Path $PID_FILE) {
    warn "Des services sont peut-etre deja en cours. Arret prealable..."
    & "$ROOT_DIR\stop.ps1" 2>$null
}

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
"" | Set-Content $PID_FILE

# ---- Espace disque --------------------------------------------------
info "Verification de l'espace disque..."
$drive     = Split-Path -Qualifier $ROOT_DIR
$freeBytes = (Get-PSDrive ($drive.TrimEnd(':'))).Free
$freeGB    = [math]::Round($freeBytes / 1GB, 1)

if ($freeBytes -lt 6GB) {
    fail @"
Espace disque insuffisant : ${freeGB} GB disponible, minimum 6 GB requis.
torch + transformers pesent ~4-5 GB.

Liberez de l'espace sur $drive puis relancez le script.
"@
}
ok "Espace disque : ${freeGB} GB disponible."

# ---- Environnement Python (venv) ------------------------------------
info "Configuration de l'environnement Python (venv)..."

if (-not (Test-Path "$VENV\Scripts\python.exe")) {
    info "Creation du venv..."
    & $PYTHON -m venv $VENV
}

$PYTHON_VENV = "$VENV\Scripts\python.exe"
$UVICORN     = "$VENV\Scripts\uvicorn.exe"

info "Mise a jour de pip..."
# Sur Windows, pip ne peut pas se mettre a jour lui-meme via pip.exe -- utiliser python -m pip
& $PYTHON_VENV -m pip install --quiet --upgrade pip

info "Installation des dependances Python..."
& $PYTHON_VENV -m pip install --quiet fastapi "uvicorn[standard]" sqlalchemy pymysql groq requests numpy scikit-learn

$pipList = (& $PYTHON_VENV -m pip list --format=freeze 2>$null) -join "`n"
if ($pipList -notmatch "(?i)^torch==") {
    info "Installation de torch (peut etre long, ~2 GB)..."
    & $PYTHON_VENV -m pip install torch --index-url https://download.pytorch.org/whl/cpu
}
if ($pipList -notmatch "(?i)^transformers==") {
    info "Installation de transformers..."
    & $PYTHON_VENV -m pip install transformers
}

ok "Dependances Python OK."

# ---- Frontend (npm) -------------------------------------------------
info "Installation des dependances frontend (npm)..."
Set-Location "$ROOT_DIR\sp500_front"
npm install --silent
ok "npm install OK."
Set-Location $ROOT_DIR

# ---- Lancement des services -----------------------------------------
function Start-Service {
    param($name, $dir, $port, $uvicornArgs)
    $log    = "$LOG_DIR\$name.log"
    $logErr = "$LOG_DIR\${name}_err.log"
    info "Demarrage de $name (port $port)..."

    $proc = Start-Process `
        -FilePath $UVICORN `
        -ArgumentList $uvicornArgs `
        -WorkingDirectory "$ROOT_DIR\$dir" `
        -RedirectStandardOutput $log `
        -RedirectStandardError  $logErr `
        -WindowStyle Hidden `
        -PassThru

    # Passer la cle Groq via variable d'environnement du process
    [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", $env:GROQ_API_KEY, "Process")

    "$name $($proc.Id)" | Add-Content $PID_FILE

    $started = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep 1
        try {
            $null = Invoke-WebRequest "http://localhost:$port/docs" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
            $started = $true; break
        } catch {}
        try {
            $null = Invoke-WebRequest "http://localhost:$port/health" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
            $started = $true; break
        } catch {}
    }

    if ($started) {
        ok "$name demarre  ->  http://localhost:$port   (PID $($proc.Id))"
    } else {
        warn "$name PID $($proc.Id) -- pas encore de reponse sur le port $port (verifier $log)"
    }
}

Start-Service "sp500_back" "sp500_back" 8000 "main:app --port 8000"
Start-Service "sp500_ml"   "sp500_ml"   8002 "main:app --port 8002"
Start-Service "sp500_ia"   "sp500_ia"   8001 "main:app --port 8001"

# Frontend
info "Demarrage du frontend Vue (port 5173)..."
$frontProc = Start-Process `
    -FilePath "npm" `
    -ArgumentList "run", "dev", "--", "--host" `
    -WorkingDirectory "$ROOT_DIR\sp500_front" `
    -RedirectStandardOutput "$LOG_DIR\sp500_front.log" `
    -RedirectStandardError  "$LOG_DIR\sp500_front_err.log" `
    -WindowStyle Hidden `
    -PassThru

"sp500_front $($frontProc.Id)" | Add-Content $PID_FILE

$started = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep 1
    try {
        $null = Invoke-WebRequest "http://localhost:5173" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        $started = $true; break
    } catch {}
}
if ($started) {
    ok "sp500_front demarre  ->  http://localhost:5173   (PID $($frontProc.Id))"
} else {
    warn "sp500_front PID $($frontProc.Id) -- pas encore de reponse (verifier $LOG_DIR\sp500_front.log)"
}

# ---- Resume ---------------------------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Tous les services sont lances !"           -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend    ->  http://localhost:5173"      -ForegroundColor Cyan
Write-Host "  API Back    ->  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Service IA  ->  http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "  Service ML  ->  http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Logs        ->  $LOG_DIR\"                  -ForegroundColor Yellow
Write-Host "  Arret       ->  .\stop.ps1"                 -ForegroundColor Yellow
Write-Host ""
