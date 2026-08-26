$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$ComposeCmd = $null
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    & docker compose version *>$null
    if ($LASTEXITCODE -eq 0) {
        $ComposeCmd = "docker compose"
    }
}
if (-not $ComposeCmd -and (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    $ComposeCmd = "docker-compose"
}

if (-not $ComposeCmd) {
    Write-Error "Neither 'docker compose' nor 'docker-compose' was found."
    Read-Host "Press Enter to continue..."
    exit 1
}

$runningServices = & ($ComposeCmd.Split()[0]) ($ComposeCmd.Split()[1..($ComposeCmd.Split().Length-1)] + @("ps", "--services", "--filter", "status=running")) 2>$null
if ($runningServices -split "`r?`n" -contains "flask") {
    Write-Host "Running fill_mongo_projects.py inside running 'flask' container..."
    & ($ComposeCmd.Split()[0]) ($ComposeCmd.Split()[1..($ComposeCmd.Split().Length-1)] + @("exec", "flask", "python", "fill_mongo_projects.py", "--owner", "x") + $args)
} else {
    Write-Host "'flask' container is not running. Running via temporary container..."
    & ($ComposeCmd.Split()[0]) ($ComposeCmd.Split()[1..($ComposeCmd.Split().Length-1)] + @("run", "--rm", "flask", "python", "fill_mongo_projects.py", "--owner", "x") + $args)
}

Read-Host "Press Enter to continue..."
