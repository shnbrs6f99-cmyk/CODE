param(
    [string]$Executable = "dist\InterestStatementGeneratorPro\InterestStatementGeneratorPro.exe",
    [int]$ObservationSeconds = 8
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
    throw "Executable not found: $Executable"
}

$resolvedExecutable = (Resolve-Path -LiteralPath $Executable).Path
$process = Start-Process -FilePath $resolvedExecutable -PassThru -WindowStyle Hidden

try {
    Start-Sleep -Seconds $ObservationSeconds
    $process.Refresh()
    if ($process.HasExited) {
        throw "Packaged executable exited during launch test with code $($process.ExitCode)."
    }
    Write-Host "Packaged executable launched successfully and remained running for $ObservationSeconds seconds (PID $($process.Id))."
}
finally {
    $process.Refresh()
    if (-not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
        $process.WaitForExit()
        Write-Host "Packaged executable terminated after successful launch verification."
    }
}
