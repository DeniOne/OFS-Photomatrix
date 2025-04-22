# Полный хард-ресет Vite 
# Используй при серьезных проблемах с кешированием

# Устанавливаем кодировку и цвета
$host.UI.RawUI.BackgroundColor = "Black"
$host.UI.RawUI.ForegroundColor = "Cyan"
Clear-Host
Write-Host "ПОЛНЫЙ ХАРД-РЕСЕТ VITE" -ForegroundColor Yellow
Write-Host "======================" -ForegroundColor Yellow
Write-Host "Этот скрипт очистит ВСЕ кеши и временные файлы Vite" -ForegroundColor Red

# Останавливаем все процессы Node
Write-Host "[1/6] Останавливаем все процессы Node..." -ForegroundColor White
Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object { 
    Write-Host "  Закрываем процесс Node PID: $($_.Id)" -ForegroundColor Gray
    $_ | Stop-Process -Force
}

# Удаляем кеш Vite
Write-Host "[2/6] Удаляем кеш Vite..." -ForegroundColor White
$pathsToClean = @(
    "node_modules/.vite",
    "node_modules/.cache",
    "node_modules/.rollup.cache",
    "node_modules/.eslintcache"
)

foreach ($path in $pathsToClean) {
    if (Test-Path $path) {
        Write-Host "  Удаляем: $path" -ForegroundColor Gray
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
    }
}

# Очищаем кеш браузера (для Chrome)
Write-Host "[3/6] Очищаем кеш браузера..." -ForegroundColor White
Write-Host "  ВАЖНО: Вручную очистите кеш браузера!" -ForegroundColor Magenta
Write-Host "  Chrome: Ctrl+Shift+Del -> 'Кешированные изображения и файлы'" -ForegroundColor Gray
Write-Host "  Firefox: Ctrl+Shift+Del -> 'Кеш'" -ForegroundColor Gray
Start-Sleep -Seconds 1

# Перезапускаем Vite с опцией --force
Write-Host "[4/6] Пересоздаем node_modules/.vite..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path "node_modules/.vite" | Out-Null

# Обновляем зависимости если есть проблемы
Write-Host "[5/6] Проверяем зависимости..." -ForegroundColor White
$doInstall = $host.UI.PromptForChoice(
    "", 
    "Обновить зависимости? (Выполнить npm install --force) Рекомендуется при серьезных ошибках.", 
    @("&Да", "&Нет"), 
    1
)
if ($doInstall -eq 0) {
    Write-Host "  Запускаем npm install --force..." -ForegroundColor Gray
    npm install --force
    Write-Host "  Установка завершена!" -ForegroundColor Green
}

# Запускаем Vite с чистого листа
Write-Host "[6/6] Запускаем Vite с чистого листа..." -ForegroundColor White
Write-Host "`nСтартуем dev-server с флагом --force..." -ForegroundColor Green
npm run dev -- --force 