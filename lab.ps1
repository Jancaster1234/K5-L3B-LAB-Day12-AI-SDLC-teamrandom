param(
    [ValidateSet('setup', 'test', 'play', 'headless')]
    [string]$Action = 'test',
    [ValidateSet('gather', 'quan')]
    [string]$Mode = 'gather',
    [int]$Seed = 1,
    [int]$Ticks = 600,
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$labPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$labPython3 = Join-Path $PSScriptRoot '.venv\Scripts\python3.exe'
Push-Location $PSScriptRoot
$labOldPath = $env:PATH
$labOldPythonPath = $env:PYTHONPATH
$labOldEncoding = $env:PYTHONIOENCODING
$labExitCode = 0
try {
    $env:PYTHONIOENCODING = 'utf-8'
    if ($Action -eq 'setup') {
        if (-not (Test-Path -LiteralPath $labPython)) {
            python -m venv .venv
            if ($LASTEXITCODE -ne 0) { throw 'Could not create .venv. Install Python 3 and retry.' }
        }
        # The supplied contract invokes python3; Windows venvs provide python.exe.
        if (-not (Test-Path -LiteralPath $labPython3)) {
            Copy-Item -LiteralPath $labPython -Destination $labPython3
        }
        & $labPython3 --version
        if ($LASTEXITCODE -ne 0) { throw 'The Python environment is not working.' }
        Write-Host 'Ready. Run: .\lab.ps1 test or .\lab.ps1 play'
    } else {
        if (-not (Test-Path -LiteralPath $labPython3)) { throw 'Run .\lab.ps1 setup first.' }
        $env:PATH = "$(Join-Path $PSScriptRoot '.venv\Scripts');$labOldPath"
        $env:PYTHONPATH = "$(Join-Path $PSScriptRoot 'tests');$PSScriptRoot"
        switch ($Action) {
            'test' { & $labPython -m unittest discover -s tests -v }
            'play' { & $labPython -m chonoi.live --mode $Mode --seed $Seed --port $Port }
            'headless' {
                New-Item -ItemType Directory -Path .local -Force | Out-Null
                & $labPython -m chonoi.headless --mode $Mode --seed $Seed --ticks $Ticks --out ".local/$Mode.jsonl"
            }
        }
        $labExitCode = $LASTEXITCODE
    }
} finally {
    $env:PATH = $labOldPath
    $env:PYTHONPATH = $labOldPythonPath
    $env:PYTHONIOENCODING = $labOldEncoding
    Pop-Location
}
exit $labExitCode
