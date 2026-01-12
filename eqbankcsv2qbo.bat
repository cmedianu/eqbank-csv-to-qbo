@echo off
REM Convert EQ Bank CSV to QBO format
REM Usage: eqbankcsv2qbo.bat <csv_file>

if "%~1"=="" (
    echo Usage: %~nx0 ^<csv_file^>
    echo Example: %~nx0 "400000395 Details.csv"
    exit /b 1
)

uv run eqbankcsv2qbo.py "%~1"
