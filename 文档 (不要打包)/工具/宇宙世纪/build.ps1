$ErrorActionPreference='Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
Push-Location $workspace
try {
    $env:PYTHONIOENCODING='utf-8'
    foreach ($script in @('inventory.py','resolve_inventory.py','derive_exclusions.py')) {
        python -B (Join-Path $PSScriptRoot $script)
        if ($LASTEXITCODE -ne 0) { throw "UC build failed: $script" }
    }
    & (Join-Path $PSScriptRoot 'render_warning.ps1')
    foreach ($script in @('build_uc.py','verify_uc.py')) {
        python -B (Join-Path $PSScriptRoot $script)
        if ($LASTEXITCODE -ne 0) { throw "UC build failed: $script" }
    }
} finally { Pop-Location }
