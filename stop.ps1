# ============================================================
#  S&P 500 Analysis Platform — Stop Script
#  Windows PowerShell
# ============================================================

$ROOT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PID_FILE = "$ROOT_DIR\.pids"

function ok   { param($msg) Write-Host "[OK]  $msg" -ForegroundColor Green  }
function warn { param($msg) Write-Host "[!!]  $msg" -ForegroundColor Yellow }

if (-not (Test-Path $PID_FILE)) {
    warn "Aucun fichier .pids trouve -- services peut-etre deja arretes."
    exit 0
}

Get-Content $PID_FILE |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
    ForEach-Object {
        # Split on one-or-more whitespace and remove empty tokens
        $parts = ($_ -split '\s+') | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

        if ($parts.Length -lt 2) {
            warn "Ligne mal formee dans .pids, ignoree: '$($_)'"
            return
        }

        $name      = $parts[0]
        $procIdStr = $parts[1]
        $procId    = 0

        if (-not [int]::TryParse($procIdStr, [ref]$procId) -or $procId -le 0) {
            warn "PID invalide dans .pids pour '$name', ignore: '$procIdStr'"
            return
        }

        try {
            $proc = Get-Process -Id $procId -ErrorAction Stop
            Stop-Process -Id $procId -Force
            ok "Arrete : $name (PID $procId)"
        } catch {
            warn "Deja arrete ou introuvable : $name (PID $procId)"
        }
    }

Remove-Item $PID_FILE -Force
Write-Host ""
ok "Tous les services arretes."
Write-Host ""
Write-Host "  Pour arreter MySQL (Docker) :"
Write-Host "    docker stop my_sp500_db"
Write-Host ""
