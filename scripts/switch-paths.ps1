param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Local", "Remote")]
    [string]$Mode
)

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$pythonScript = Join-Path $scriptDir "switch-paths.py"

if (-not (Test-Path $pythonScript)) {
    throw "switch-paths.py not found: $pythonScript"
}

python $pythonScript $Mode
if ($LASTEXITCODE -ne 0) {
    throw "switch-paths failed with exit code $LASTEXITCODE"
}
