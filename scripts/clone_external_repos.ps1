param(
    [string]$NavUrl = "https://github.com/66Lau/NEXTE_Sentry_Nav.git",
    [string]$PrmsUrl = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ThirdParty = Join-Path $RepoRoot "third_party"
New-Item -ItemType Directory -Force -Path $ThirdParty | Out-Null

$NavDir = Join-Path $ThirdParty "NEXTE_Sentry_Nav"
if (-not (Test-Path -LiteralPath $NavDir)) {
    git clone $NavUrl $NavDir
}

if ($PrmsUrl -ne "") {
    $PrmsDir = Join-Path $ThirdParty "prms"
    if (-not (Test-Path -LiteralPath $PrmsDir)) {
        git clone $PrmsUrl $PrmsDir
    }
}

Write-Host "External repositories are ready under $ThirdParty"

