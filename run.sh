#!/bin/bash

echo "=== Adobe Hackathon - Document Intelligence Pipeline ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed or not in PATH"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run the complete pipeline"
    echo "  parse       Parse PDF files only"
    echo "  shell       Open interactive shell in container"
    echo "  clean       Clean up Docker resources"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 parse /app/input/document.pdf /app/input/parsed.json"
    echo "  $0 shell"
}

# Build Docker image
build_image() {
    echo "Building Docker image..."
    docker-compose build
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully"
    else
        echo "❌ Failed to build Docker image"
        exit 1
    fi
}

# Run the complete pipeline
run_pipeline() {
    echo "Running document intelligence pipeline..."
    echo "Input directory: ./app/input"
    echo "Output directory: ./app/output"
    
    # Ensure directories exist
    mkdir -p app/input app/output
    
    # Check if input JSON exists
    if [ ! -f "app/input/challenge1b_input.json" ]; then
        echo "⚠️  Warning: app/input/challenge1b_input.json not found"
        echo "Please create this file with your persona and job requirements"
    fi
    
    # Check for PDF files
    pdf_count=$(find app/input -name "*.pdf" -type f | wc -l)
    if [ $pdf_count -eq 0 ]; then
        echo "⚠️  Warning: No PDF files found in app/input/"
        echo "Please place your PDF files in the app/input/ directory"
    else
        echo "📄 Found $pdf_count PDF file(s) in app/input/"
    fi
    
    docker-compose up --build
    
    if [ $? -eq 0 ]; then
        echo "✅ Pipeline completed successfully"
        echo "📊 Check app/output/ for results"
    else
        echo "❌ Pipeline failed"
        exit 1
    fi
}

# Parse specific PDF file
parse_pdf() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: $0 parse INPUT_PDF OUTPUT_JSON"
        echo "Example: $0 parse /app/input/document.pdf /app/input/parsed.json"
        exit 1
    fi
    
    echo "Parsing PDF: $1"
    docker-compose run --rm document-intelligence python -m src.parser --input "$1" --output "$2"
}

# Open interactive shell
open_shell() {
    echo "Opening interactive shell in container..."
    docker-compose run --rm document-intelligence /bin/bash
}

# Clean up Docker resources
clean_up() {
    echo "Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Cleanup completed"
}

# Main script logic
case "$1" in
    "build")
        build_image
        ;;
    "run")
        run_pipeline
        ;;
    "parse")
        parse_pdf "$2" "$3"
        ;;
    "shell")
        open_shell
        ;;
    "clean")
        clean_up
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    "")
        echo "No command specified. Running complete pipeline..."
        run_pipeline
        ;;
    *)
        echo "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 