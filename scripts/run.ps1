$root = Join-Path $PSScriptRoot ".."
$venvPython = Join-Path $root ".venv\\Scripts\\python.exe"
$python = "python"
if (Test-Path $venvPython) {
  $python = $venvPython
}
Set-Location -Path $root
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 9999
