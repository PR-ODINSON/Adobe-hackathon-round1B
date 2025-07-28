@echo off
echo === Adobe Hackathon - Document Intelligence Pipeline ===

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not in PATH
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: docker-compose is not installed or not in PATH
    exit /b 1
)

if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="parse" goto parse
if "%1"=="shell" goto shell
if "%1"=="clean" goto clean
if "%1"=="help" goto usage
if "%1"=="-h" goto usage
if "%1"=="--help" goto usage
if "%1"=="" goto run
goto unknown

:usage
echo Usage: %0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo   build       Build the Docker image
echo   run         Run the complete pipeline
echo   parse       Parse PDF files only
echo   shell       Open interactive shell in container
echo   clean       Clean up Docker resources
echo.
echo Examples:
echo   %0 build
echo   %0 run
echo   %0 parse /app/input/document.pdf /app/input/parsed.json
echo   %0 shell
goto end

:build
echo Building Docker image...
docker-compose build
if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully
) else (
    echo ❌ Failed to build Docker image
    exit /b 1
)
goto end

:run
echo Running document intelligence pipeline...
echo Input directory: .\app\input
echo Output directory: .\app\output

REM Ensure directories exist
if not exist "app\input" mkdir "app\input"
if not exist "app\output" mkdir "app\output"

REM Check if input JSON exists
if not exist "app\input\challenge1b_input.json" (
    echo ⚠️  Warning: app\input\challenge1b_input.json not found
    echo Please create this file with your persona and job requirements
)

REM Check for PDF files
set pdf_count=0
for %%f in (app\input\*.pdf) do set /a pdf_count+=1
if %pdf_count% equ 0 (
    echo ⚠️  Warning: No PDF files found in app\input\
    echo Please place your PDF files in the app\input\ directory
) else (
    echo 📄 Found %pdf_count% PDF file(s) in app\input\
)

docker-compose up --build

if %errorlevel% equ 0 (
    echo ✅ Pipeline completed successfully
    echo 📊 Check app\output\ for results
) else (
    echo ❌ Pipeline failed
    exit /b 1
)
goto end

:parse
if "%2"=="" goto parse_usage
if "%3"=="" goto parse_usage
echo Parsing PDF: %2
docker-compose run --rm document-intelligence python -m src.parser --input "%2" --output "%3"
goto end

:parse_usage
echo Usage: %0 parse INPUT_PDF OUTPUT_JSON
echo Example: %0 parse /app/input/document.pdf /app/input/parsed.json
goto end

:shell
echo Opening interactive shell in container...
docker-compose run --rm document-intelligence /bin/bash
goto end

:clean
echo Cleaning up Docker resources...
docker-compose down --rmi all --volumes --remove-orphans
echo ✅ Cleanup completed
goto end

:unknown
echo Unknown command: %1
goto usage

:end 