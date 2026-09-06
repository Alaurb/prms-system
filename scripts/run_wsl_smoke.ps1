param(
    [string]$Distro = "Ubuntu-20.04",
    [string]$Workspace = "~/prms_ws"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$LinuxRepoRoot = $RepoRoot -replace "\\", "/"
$LinuxRepoRoot = $LinuxRepoRoot -replace "^C:", "/mnt/c"

$Script = "$LinuxRepoRoot/scripts/run_smoke.sh"
wsl.exe -d $Distro -- bash $Script $Workspace $LinuxRepoRoot
