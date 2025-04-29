@echo off
echo =================================================
echo = Создание .env файла из примера                 =
echo =================================================
echo.

IF EXIST .env (
  echo Файл .env уже существует!
  echo Хотите заменить его? (y/n)
  set /p ANSWER=
  IF /I "%ANSWER%"=="y" (
    copy .env.example .env /Y
    echo Файл .env успешно заменен!
  ) ELSE (
    echo Операция отменена.
  )
) ELSE (
  copy .env.example .env
  echo Файл .env создан из примера. Пожалуйста, отредактируйте его!
)

echo.
echo Нажмите любую клавишу для выхода...
pause > nul 