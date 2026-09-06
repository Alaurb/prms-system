param(
    [string]$Distro = "Ubuntu-20.04",
    [string]$Workspace = "~/prms_ws"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
if ($RepoRoot -match "^([A-Za-z]):\\(.*)$") {
    $Drive = $Matches[1].ToLowerInvariant()
    $Rest = $Matches[2] -replace "\\", "/"
    $LinuxRepoRoot = "/mnt/$Drive/$Rest"
} else {
    throw "Unsupported repository path: $RepoRoot"
}

$Script = "$LinuxRepoRoot/scripts/run_map_smoke.sh"
wsl.exe -d $Distro -- bash $Script $Workspace $LinuxRepoRoot
