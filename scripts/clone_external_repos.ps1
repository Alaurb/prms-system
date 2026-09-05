param(
    [string]$NavUrl = "https://github.com/66Lau/NEXTE_Sentry_Nav.git",
    [string]$PrmsUrl = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ThirdParty = Join-Path $RepoRoot "third_party"
New-Item -ItemType Directory -Force -Path $ThirdParty | Out-Null

$NavDir = Join-Path $ThirdParty "NEXTE_Sentry_Nav_src"
if (-not (Test-Path -LiteralPath $NavDir)) {
    git clone --depth 1 $NavUrl $NavDir
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to clone navigation repository: $NavUrl"
    }
}

if ($PrmsUrl -ne "") {
    $PrmsDir = Join-Path $ThirdParty "prms"
    if (-not (Test-Path -LiteralPath $PrmsDir)) {
        git clone $PrmsUrl $PrmsDir
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to clone PRMS repository: $PrmsUrl"
        }
    }
}

Write-Host "External repositories are ready under $ThirdParty"
