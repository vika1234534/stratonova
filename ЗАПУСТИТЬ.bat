@echo off
chcp 65001 >nul
title Система учёта ресурсов — ТК Новочебоксарский

echo ╔══════════════════════════════════════════════════╗
echo ║   Система учёта ресурсов ООО ТК Новочебоксарский ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: Переходим в папку где лежит этот файл
cd /d "%~dp0"

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo.
    echo Установи Python с сайта: https://python.org/downloads
    echo Обязательно поставь галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Устанавливаем библиотеки если нужно
echo Проверка библиотек...
pip install customtkinter mysql-connector-python reportlab --quiet --disable-pip-version-check

echo.
echo Запуск программы...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Программа завершилась с ошибкой.
    echo Возможные причины:
    echo   1. MySQL не запущен
    echo   2. Неверный пароль в database\db.py
    echo   3. База данных не создана
    echo.
    pause
)
