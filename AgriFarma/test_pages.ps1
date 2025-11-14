# Quick Route Checker - Tests if pages load without 500 errors
$urls = @(
    @{url="/"; name="Homepage"},
    @{url="/auth/login"; name="Login Page"},
    @{url="/auth/register"; name="Register Page"},
    @{url="/forum/"; name="Forum Index"},
    @{url="/blog/"; name="Blog Index"},
    @{url="/marketplace/"; name="Marketplace Index"},
    @{url="/consultancy/"; name="Consultancy Directory"}
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AGRIFARMA ROUTE TESTING" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

foreach ($test in $urls) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000$($test.url)" -UseBasicParsing -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline
            Write-Host " $($test.name) - Status 200"
            $passed++
        } else {
            Write-Host "[WARN]" -ForegroundColor Yellow -NoNewline
            Write-Host " $($test.name) - Status: $($response.StatusCode)"
            $passed++
        }
    } catch {
        Write-Host "[FAIL]" -ForegroundColor Red -NoNewline
        Write-Host " $($test.name) - ERROR"
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Results: $passed passed, $failed failed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -eq 0) {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed" -ForegroundColor Yellow
}
Write-Host ""
