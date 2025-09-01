#!/bin/bash

# Browser Testing Automation Script
# This script helps set up and test the application before merging

set -e

echo "🧪 Browser Testing Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the project root."
    exit 1
fi

print_status "Starting browser testing setup..."

# 1. Check Node.js and npm
print_status "Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi

print_success "Node.js $(node --version) and npm $(npm --version) are available"

# 2. Install dependencies
print_status "Installing frontend dependencies..."
npm install
print_success "Frontend dependencies installed"

# 3. Check backend environment
print_status "Checking backend environment..."
if [ ! -d "backend/venv" ]; then
    print_warning "Backend virtual environment not found. Please create it manually:"
    echo "  cd backend"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
else
    print_success "Backend virtual environment exists"
fi

# 4. Run linting
print_status "Running linting checks..."
if npm run lint; then
    print_success "Linting passed"
else
    print_warning "Linting issues found. Please fix them before proceeding."
fi

# 5. Run tests
print_status "Running tests..."
if npm test; then
    print_success "Tests passed"
else
    print_warning "Some tests failed. Please review before proceeding."
fi

# 6. Build the application
print_status "Building the application..."
if npm run build; then
    print_success "Build successful"
else
    print_error "Build failed. Please fix the issues before proceeding."
    exit 1
fi

# 7. Check if servers are running
print_status "Checking if servers are running..."

# Check if frontend dev server is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    print_success "Frontend dev server is running on http://localhost:5173"
else
    print_warning "Frontend dev server is not running. Start it with: npm run dev"
fi

# Check if backend API server is running
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    print_success "Backend API server is running on http://localhost:5000"
else
    print_warning "Backend API server is not running. Start it with: cd backend && python api_server.py"
fi

echo ""
echo "🎯 Browser Testing Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start the development server: npm run dev"
echo "2. Start the backend server: cd backend && python api_server.py"
echo "3. Open http://localhost:5173 in your browser"
echo "4. Follow the testing checklist in BROWSER_TESTING_CHECKLIST.md"
echo ""
echo "Testing URLs:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:5000"
echo "- API Health: http://localhost:5000/health"
echo ""
echo "Browser Testing Checklist:"
echo "- [ ] Test on Chrome, Firefox, Safari, Edge"
echo "- [ ] Test responsive design on different screen sizes"
echo "- [ ] Test all interactive features"
echo "- [ ] Check console for errors"
echo "- [ ] Test performance and loading times"
echo ""
echo "Happy testing! 🚀"
