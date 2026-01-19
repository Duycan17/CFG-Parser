# PowerShell curl test commands for Java CFG/DDG Parser API

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "1. Health Check" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
curl.exe -X GET "$baseUrl/health" `
  -H "Content-Type: application/json"
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "2. Analyze Simple Java Code" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$body = @{
    code = "public class Test { public int add(int a, int b) { return a + b; } }"
    include_method_graphs = $true
    include_class_graph = $false
} | ConvertTo-Json

curl.exe -X POST "$baseUrl/analyze" `
  -H "Content-Type: application/json" `
  -d $body
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "3. Analyze Complex Java Code" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
$body2 = @{
    code = "public class Calculator { public int factorial(int n) { if (n <= 1) { return 1; } int fact = 1; for (int i = 2; i <= n; i++) { fact = fact * i; } return fact; } }"
    include_method_graphs = $true
    include_class_graph = $true
} | ConvertTo-Json

curl.exe -X POST "$baseUrl/analyze" `
  -H "Content-Type: application/json" `
  -d $body2
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "4. Analyze Java File Upload" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
if (Test-Path "test_example.java") {
    curl.exe -X POST "$baseUrl/analyze/file" `
      -F "file=@test_example.java" `
      -F "include_class_graph=true" `
      -F "include_method_graphs=true"
} else {
    Write-Host "test_example.java not found, skipping file upload test" -ForegroundColor Yellow
}
Write-Host ""
