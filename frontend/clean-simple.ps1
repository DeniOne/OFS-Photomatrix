# Упрощенная версия скрипта очистки Vite

Write-Host "Останавливаем процессы Vite..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" } | ForEach-Object { 
    Write-Host "Останавливаем процесс: $($_.Id)" -ForegroundColor Yellow
    Stop-Process -Id $_.Id -Force 
}

Write-Host "Удаляем кеш Vite..." -ForegroundColor Yellow
if (Test-Path -Path "node_modules/.vite") {
    Remove-Item -Recurse -Force "node_modules/.vite"
    Write-Host "Кеш Vite удален!" -ForegroundColor Green
}

Write-Host "Запускаем Vite заново..." -ForegroundColor Green
npm run dev -- --force 