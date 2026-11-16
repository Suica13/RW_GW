param([switch]$Runtime, [switch]$TechnologyChanges, [switch]$PMC)
$ErrorActionPreference='Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$gameRoot = Split-Path (Split-Path $workspace -Parent) -Parent
$previousJavaOptions = $env:JAVA_TOOL_OPTIONS
Push-Location $workspace
try {
    & (Join-Path $PSScriptRoot 'prepare_engine.ps1')
    python -B (Join-Path $PSScriptRoot 'verify_uc.py')
    if ($LASTEXITCODE -ne 0) { throw 'UC static verification failed' }
    if ($Runtime -or $TechnologyChanges -or $PMC) {
        python -B (Join-Path $PSScriptRoot 'prepare_runtime.py')
        if ($LASTEXITCODE -ne 0) { throw 'UC runtime fixtures failed' }
        if ($TechnologyChanges) {
            python -B (Join-Path $PSScriptRoot 'prepare_technology_runtime.py')
            if ($LASTEXITCODE -ne 0) { throw 'UC technology fixtures failed' }
        }
        $compiler = Join-Path $gameRoot 'jvm64/bin/javac.exe'
        & $compiler -encoding UTF-8 -cp 'output/uc/engine/game-lib.jar;output/uc/engine/libs/*' -d output/uc/classes (Join-Path $PSScriptRoot 'UCTestMain.java')
        if ($LASTEXITCODE -ne 0) { throw 'UC runtime bridge compilation failed' }
        if ($TechnologyChanges) { $env:JAVA_TOOL_OPTIONS = ($previousJavaOptions + ' -Duc.techMergeOnly=true').Trim() }
        if ($PMC) { $env:JAVA_TOOL_OPTIONS = ($previousJavaOptions + ' -Duc.pmcOnly=true').Trim() }
        python -B (Join-Path $PSScriptRoot 'runtime_check.py')
        if ($LASTEXITCODE -ne 0) { throw 'UC runtime validation failed' }
    } else {
        python -B (Join-Path $PSScriptRoot 'engine_check.py')
        if ($LASTEXITCODE -ne 0) { throw 'UC engine load failed' }
    }
} finally {
    if ($null -eq $previousJavaOptions) { Remove-Item Env:JAVA_TOOL_OPTIONS -ErrorAction SilentlyContinue }
    else { $env:JAVA_TOOL_OPTIONS = $previousJavaOptions }
    Pop-Location
}
