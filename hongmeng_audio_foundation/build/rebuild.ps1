$ErrorActionPreference = 'Stop'
$taskRuntime = 'C:/Users/47156/.cache/codex-runtimes/codex-primary-runtime/dependencies'
$taskNode = Join-Path $taskRuntime 'node/bin/node.exe'
$taskPython = Join-Path $taskRuntime 'python/python.exe'
$artifactRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path $artifactRoot -Parent
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'node_modules'))) {
 New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot 'node_modules') -Target (Join-Path $taskRuntime 'node/node_modules') | Out-Null
}
$sourceCurrent = Join-Path $workspaceRoot 'source_gitcode'
$sourceHistoric = Join-Path $workspaceRoot 'source_audio_5_1'
# Rebuilding pages uses packaged evidence; full repos are required only to regenerate excerpts.

if ((Test-Path -LiteralPath $sourceCurrent) -and (git -C $sourceCurrent rev-parse HEAD) -ne '3a2688e805df970739e3b0cebf9cc05d8cb24e9b') { throw 'Current source SHA mismatch' }
if ((Test-Path -LiteralPath $sourceHistoric) -and (git -C $sourceHistoric rev-parse HEAD) -ne 'c42a228d60b64a90d6b05cf26278a89253e5310b') { throw 'Historical source SHA mismatch' }
& $taskPython (Join-Path $PSScriptRoot 'audio.py')
if ($LASTEXITCODE -ne 0) { throw 'Audio build failed' }
# pages/Pxx.json are the authoritative editable content. Do not rerun author snapshots after manual JSON edits.
& $taskNode (Join-Path $PSScriptRoot 'deck.mjs') all
if ($LASTEXITCODE -ne 0) { throw 'Deck build failed' }
& $taskPython (Join-Path $PSScriptRoot 'package.py')
if ($LASTEXITCODE -ne 0) { throw 'Package checks failed' }
