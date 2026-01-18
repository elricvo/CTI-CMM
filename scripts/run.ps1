$root = Join-Path $PSScriptRoot ".."
$useTestData = $args -contains "--test-data"
$venvPython = Join-Path $root ".venv\\Scripts\\python.exe"
$python = "python"
if (Test-Path $venvPython) {
  $python = $venvPython
}
Set-Location -Path $root
if ($useTestData) {
  $env:APP_TEST_DATA = "1"
  $env:APP_DATA_DIR = Join-Path $root "data-test"
}
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 9999
