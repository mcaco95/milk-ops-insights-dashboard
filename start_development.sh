#!/bin/bash

echo "🚀 Starting Dairy Operations Development Environment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Test the setup
echo "🧪 Testing database setup..."
python test_setup.py

# Show service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🗄️  Database: localhost:5432"
echo ""
echo "👤 Login credentials:"
echo "   Admin: admin / admin123"
echo "   Milky Way: milkyway / password123"
echo "   T&K Dairy: tkdairy / password123"
echo ""
echo "📝 To view logs:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down" 