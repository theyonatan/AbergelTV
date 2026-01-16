@echo off
setlocal EnableDelayedExpansion

REM ===== CONFIG =====
set OUTPUT_DIR=output
set CRF=20
set PRESET=veryfast

REM ==================

if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
)

for /R %%F in (*.mkv *.avi *.mov *.wmv *.flv *.webm) do (
    set "INPUT=%%F"

    REM Get relative path
    set "REL=%%F"
    set "REL=!REL:%CD%\=!"

    REM Build output path
    set "OUT=%OUTPUT_DIR%!REL!"
    set "OUT=!OUT:~0,-4!.mp4"

    REM Create output directories
    for %%D in ("!OUT!") do (
        if not exist "%%~dpD" mkdir "%%~dpD"
    )

    REM Skip if already converted
    if exist "!OUT!" (
        echo SKIP: %%F
    ) else (
        echo CONVERT: %%F
        ffmpeg -y -i "%%F" ^
            -map 0:v:0 -map 0:a? ^
            -c:v libx264 -pix_fmt yuv420p ^
            -preset %PRESET% -crf %CRF% ^
            -c:a aac -b:a 192k ^
            "!OUT!"
    )
)

echo.
echo DONE!
pause
