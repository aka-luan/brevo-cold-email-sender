$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$logsDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

$logFile = Join-Path $logsDir "cron.log"
$python = Join-Path $PSScriptRoot ".venv\\Scripts\\python.exe"

if (-not (Test-Path $python)) {
    throw "Python da virtualenv não encontrado em $python"
}

$dryRunFlag = @()
if ($env:PROSPECTAAI_DRY_RUN -eq "1") {
    $dryRunFlag = @("--dry-run")
}

$commands = @(
    ,(@("campaign.py", "send", "--limit", "30") + $dryRunFlag),
    ,(@("campaign.py", "followup") + $dryRunFlag)
)

foreach ($commandArgs in $commands) {
    & $python @commandArgs 2>&1 | Tee-Object -FilePath $logFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar: $python $($commandArgs -join ' ')"
    }
}
