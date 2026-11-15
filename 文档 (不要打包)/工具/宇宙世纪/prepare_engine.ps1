$ErrorActionPreference='Stop'
$workspace = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
$gameRoot = Split-Path (Split-Path $workspace -Parent) -Parent
$testEngine = Join-Path $workspace 'output/uc/engine'
New-Item -ItemType Directory -Path $testEngine -Force | Out-Null
foreach ($name in @('assets','font','libs','res')) {
    $link = Join-Path $testEngine $name
    if (!(Test-Path -LiteralPath $link)) { New-Item -ItemType Junction -Path $link -Target (Join-Path $gameRoot $name) | Out-Null }
}
foreach ($file in (Get-ChildItem -LiteralPath $gameRoot -File | Where-Object { $_.Name -eq 'game-lib.jar' -or $_.Extension -eq '.dll' })) {
    $target = Join-Path $testEngine $file.Name
    if (!(Test-Path -LiteralPath $target)) { Copy-Item -LiteralPath $file.FullName -Destination $target }
}
$settings = Join-Path $testEngine 'preferences.ini'
if (!(Test-Path -LiteralPath $settings)) {
    $original = Join-Path $gameRoot 'preferences.ini'
    if (Test-Path -LiteralPath $original) { Copy-Item -LiteralPath $original -Destination $settings }
    else { '[settings]' | Set-Content -LiteralPath $settings -Encoding UTF8 }
}
$modRoot = Join-Path $testEngine 'mods/units'
New-Item -ItemType Directory -Path $modRoot -Force | Out-Null
$allowed = @('GW_BattleUniverse_Main','GW_BattleUniverse_DLC_UC')
foreach ($entry in (Get-ChildItem -LiteralPath $modRoot)) {
    if ($entry.Name -notin $allowed) { throw "Unexpected mod in isolation area: $($entry.FullName)" }
}
foreach ($name in $allowed) {
    $link = Join-Path $modRoot $name
    if (!(Test-Path -LiteralPath $link)) { New-Item -ItemType Junction -Path $link -Target (Join-Path $workspace $name) | Out-Null }
}
