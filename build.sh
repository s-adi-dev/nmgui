#!/usr/bin/env bash

# Robust and optimized build script for Nuitka compilation
# Exit on any error, undefined variables, or pipe failures
set -euo pipefail

# Configuration
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SRC_DIR="${PROJECT_ROOT}/src"
readonly DIST_DIR="${PROJECT_ROOT}/dist"
readonly MAIN_MODULE="nmgui"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Cleanup function for trap
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_error "Build failed with exit code $exit_code"
    fi
    # Return to original directory
    cd "${PROJECT_ROOT}"
    exit $exit_code
}

# Set trap for cleanup
trap cleanup EXIT

# Validation functions
check_dependencies() {
    local missing_deps=()
    
    if ! command -v nuitka >/dev/null 2>&1; then
        missing_deps+=("nuitka")
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Please install them before running this script"
        exit 1
    fi
}

validate_project_structure() {
    if [[ ! -d "${SRC_DIR}" ]]; then
        log_error "Source directory '${SRC_DIR}' not found"
        exit 1
    fi
    
    if [[ ! -f "${SRC_DIR}/${MAIN_MODULE}/__main__.py" ]] && [[ ! -f "${SRC_DIR}/${MAIN_MODULE}.py" ]]; then
        log_error "Main module '${MAIN_MODULE}' not found"
        exit 1
    fi
}

# Build functions
clean_dist() {
    log_info "Cleaning distribution directory..."
    if [[ -d "${DIST_DIR}" ]]; then
        rm -rf "${DIST_DIR}"
    fi
    mkdir -p "${DIST_DIR}"
}

build_application() {
    log_info "Starting Nuitka compilation..."
    
    # Change to source directory
    cd "${SRC_DIR}"
    
    # Build nuitka command with optimizations
    local nuitka_cmd=(
        nuitka
        --standalone
        --onefile
        --include-package-data=gi
        --include-module=nmcli
        --follow-imports
        --output-dir="../dist"
        --remove-output
        --assume-yes-for-downloads
        --warn-implicit-exceptions
        --warn-unusual-code
    )
    
    # Add optimization flags
    nuitka_cmd+=(
        --lto=yes
        --jobs="$(nproc 2>/dev/null || echo 4)"
    )
    
    # Add the main module
    nuitka_cmd+=("${MAIN_MODULE}")
    
    # Execute the build
    log_info "Running: ${nuitka_cmd[*]}"
    "${nuitka_cmd[@]}"
    
    # Return to project root
    cd "${PROJECT_ROOT}"
}

verify_build() {
    local executable_name="nmgui.bin"
    local executable_path="${DIST_DIR}/${executable_name}"
    
    if [[ -f "${executable_path}" ]]; then
        log_info "Build successful! Executable created: ${executable_path}"
        log_info "Executable size: $(du -h "${executable_path}" | cut -f1)"
        
        # Make sure it's executable
        chmod +x "${executable_path}"
        
        return 0
    else
        log_error "Build failed: executable not found at ${executable_path}"
        return 1
    fi
}

# Main execution
main() {
    log_info "Starting build process..."
    
    # Validate environment
    check_dependencies
    validate_project_structure
    
    # Build process
    clean_dist
    build_application
    verify_build
    
    log_info "Build process completed successfully!"
}

# Run main function
main "$@"