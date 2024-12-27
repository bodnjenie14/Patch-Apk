@echo off
setlocal enabledelayedexpansion

:::::::::::::::::::::::::::::::::::::
:: Setting Variables
:::::::::::::::::::::::::::::::::::::
set INPUT_FILENAME=%1
set NEW_GAMESERVER_URL=%2
set NEW_DLCSERVER_URL=%3

if "%INPUT_FILENAME%"=="" (
    echo Usage: %0 [INPUT_FILENAME] [NEW_GAMESERVER_URL] [NEW_DLCSERVER_URL]
    exit /b 1
)

if "%NEW_GAMESERVER_URL%"=="" (
    echo Usage: %0 [INPUT_FILENAME] [NEW_GAMESERVER_URL] [NEW_DLCSERVER_URL]
    exit /b 1
)

if "%NEW_DLCSERVER_URL%"=="" (
    echo Usage: %0 [INPUT_FILENAME] [NEW_GAMESERVER_URL] [NEW_DLCSERVER_URL]
    exit /b 1
)

:::::::::::::::::::::::::::::::::::::
:: Installing Dependencies
:::::::::::::::::::::::::::::::::::::
if not exist apktool_2.10.0.jar (
    echo Downloading apktool...
    powershell -Command "Invoke-WebRequest -Uri https://github.com/iBotPeaches/Apktool/releases/download/v2.10.0/apktool_2.10.0.jar -OutFile apktool_2.10.0.jar"
)

if not exist venv\Scripts\pip.exe (
    echo Creating venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        exit /b 1
    )

    echo Installing pip dependencies...
    venv\Scripts\pip install buildapp
    if %errorlevel% neq 0 (
        exit /b 1
    )
    venv\Scripts\buildapp_fetch_tools
    if %errorlevel% neq 0 (
        exit /b 1
    )
)

:::::::::::::::::::::::::::::::::::::
:: Decompile App
:::::::::::::::::::::::::::::::::::::
echo Decompiling apk...
java -jar apktool_2.10.0.jar d %INPUT_FILENAME% -o tappedout
if %errorlevel% neq 0 (
    exit /b 1
)

:::::::::::::::::::::::::::::::::::::
:: Change Server URLs
:::::::::::::::::::::::::::::::::::::
echo Replacing server urls (this can take a long time)...

echo Replacing GameServer URLs...
powershell -Command "Get-ChildItem -Recurse -Path tappedout\* | ForEach-Object { (Get-Content $_.FullName) -replace 'https://prod.simpsons-ea.com', '%NEW_GAMESERVER_URL%' | Set-Content $_.FullName }"

echo Replacing Director API URLs...
powershell -Command "Get-ChildItem -Recurse -Path tappedout\* | ForEach-Object { (Get-Content $_.FullName) -replace 'https://syn-dir.sn.eamobile.com', '%NEW_GAMESERVER_URL%' | Set-Content $_.FullName }"

echo Replacing DLC Server URLs...
powershell -Command "Get-ChildItem -Recurse -Path tappedout\* | ForEach-Object { (Get-Content $_.FullName) -replace 'https://oct2018-4-35-0-uam5h44a.tstodlc.eamobile.com/netstorage/gameasset/direct/simpsons/', '%NEW_DLCSERVER_URL%' | Set-Content $_.FullName }"


:::::::::::::::::::::::::::::::::::::
:: Recompile App
:::::::::::::::::::::::::::::::::::::
echo Recompiling app...
venv\Scripts\buildapp -d tappedout -o "%INPUT_FILENAME%-patched.apk"
if %errorlevel% neq 0 (
    exit /b 1
)

echo Done!

