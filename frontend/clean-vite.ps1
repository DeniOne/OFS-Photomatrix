# Скрипт для полной очистки кеша Vite и перезапуска сервера разработки
# Версия 2.0 - Оптимизированная для Windows

# Цветная консоль для лучшей видимости
$colors = @{
    Green = [ConsoleColor]::Green
    Yellow = [ConsoleColor]::Yellow
    Red = [ConsoleColor]::Red
    Cyan = [ConsoleColor]::Cyan
}

# Вспомогательная функция для вывода
function Write-ColorMessage([string]$message, [ConsoleColor]$color) {
    Write-Host $message -ForegroundColor $color
}

# Шаг 1: Останавливаем все запущенные процессы Vite
Write-ColorMessage "1/5 Останавливаем запущенные процессы Vite..." $colors.Yellow
$viteProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*vite*" }
if ($viteProcesses) {
    $viteProcesses | ForEach-Object {
        Write-ColorMessage "   Остановка процесса Vite: $($_.Id)" $colors.Yellow
        Stop-Process -Id $_.Id -Force
    }
    Write-ColorMessage "   Процессы Vite успешно остановлены!" $colors.Green
} else {
    Write-ColorMessage "   Запущенных процессов Vite не найдено." $colors.Cyan
}

# Шаг 2: Удаляем кеш Vite
Write-ColorMessage "`n2/5 Удаляем кеш Vite..." $colors.Yellow
$viteCache = "node_modules/.vite"
if (Test-Path -Path $viteCache) {
    Remove-Item -Recurse -Force $viteCache
    Write-ColorMessage "   Кеш Vite успешно удален!" $colors.Green
} else {
    Write-ColorMessage "   Директория кеша Vite не найдена." $colors.Cyan
}

# Шаг 3: Дополнительная очистка кеша ESBuild
Write-ColorMessage "`n3/5 Удаляем кеш ESBuild..." $colors.Yellow
$esbuildCache = "node_modules/.esbuild-register"
if (Test-Path -Path $esbuildCache) {
    Remove-Item -Recurse -Force $esbuildCache
    Write-ColorMessage "   Кеш ESBuild успешно удален!" $colors.Green
} else {
    Write-ColorMessage "   Директория кеша ESBuild не найдена." $colors.Cyan
}

# Шаг 4: Сбрасываем модули, которые могут быть неправильно закешированы
Write-ColorMessage "`n4/5 Сбрасываем проблемные модули..." $colors.Yellow
$problemModules = @(
    "node_modules/react",
    "node_modules/react-dom",
    "node_modules/@mantine"
)

foreach ($module in $problemModules) {
    if (Test-Path -Path $module) {
        Write-ColorMessage "   Модуль $module найден. Проверяем целостность..." $colors.Cyan
    } else {
        Write-ColorMessage "   Модуль $module не найден. Возможно, требуется `npm install`." $colors.Yellow
    }
}

# Шаг 5: Запускаем Vite с оптимизированными параметрами
Write-ColorMessage "`n5/5 Запускаем Vite с оптимизированными параметрами..." $colors.Green
Write-ColorMessage "   Совет: если загрузка всё ещё медленная, попробуйте:" $colors.Cyan
Write-ColorMessage "   1. Откройте DevTools в браузере (F12)" $colors.Cyan
Write-ColorMessage "   2. Перейдите на вкладку Network" $colors.Cyan
Write-ColorMessage "   3. Установите галочку Disable cache" $colors.Cyan
Write-ColorMessage "   4. Перезагрузите страницу с зажатым Ctrl (хард-релоад)" $colors.Cyan

# Запуск Vite с принудительной очисткой кеша зависимостей
# Флаг --force заставляет Vite пересобрать кеш зависимостей
npm run dev -- --force 