# Bootstrap for Windows (PowerShell). macOS / Linux: setup_project.sh.
# All logic lives in scripts/pipeline.py (standard library only).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = $null
foreach ($candidate in @("py", "python", "python3")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) { $py = $candidate; break }
}
if (-not $py) { throw "Python 3.10+ is required (py/python not found)." }

& $py scripts/pipeline.py setup --rag-server
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $py scripts/pipeline.py doctor

Write-Host ""
Write-Host "Next steps:"
Write-Host "  .venv\Scripts\Activate.ps1"
Write-Host "  python scripts/pipeline.py build              # extract, chunk, validate, embed, import, eval"
Write-Host "  python scripts/pipeline.py build --from embed # when the chunks in output/ are current"
Write-Host "Local topology: python OmnisRAGServer/rag-server/ragserver.py, then the MCP bridge (VS Code starts it)."
