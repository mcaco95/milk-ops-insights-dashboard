# Dairy Operations Management System

A simplified, database-driven dairy operations management system that provides real-time insights into tank levels, route tracking, and volume reporting.

## 🏗️ Architecture Overview

This system has been redesigned with a **database-first approach** for better performance, reliability, and offline capabilities:

### Core Components

1. **Data Population Scripts** - Run your existing scripts (`tank_level_dashboard.py`, `get_daily_routes.py`, `get_dairy_volume.py`) and store results in PostgreSQL
2. **Scheduler Service** - Automatically runs data population scripts at appropriate intervals
3. **FastAPI Backend** - Simple CRUD operations that read directly from the database
4. **React Frontend** - Modern dashboard interface
5. **PostgreSQL Database** - Centralized data storage with proper schema

### Key Benefits

- ✅ **Fast API responses** - No more real-time script execution
- ✅ **Offline capability** - Data persists in database
- ✅ **Simplified architecture** - No complex caching or transformations
- ✅ **Reliable data** - Scripts run on schedule, not on-demand
- ✅ **Easy deployment** - Docker-based with clear separation of concerns

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and start the development environment:**
   ```bash
   git clone <repository>
   cd DairyMen
   chmod +x start_development.sh
   ./start_development.sh
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Login credentials:**
   - **Admin:** `admin` / `admin123`
   - **Milky Way Dairy:** `milkyway` / `password123`
   - **T&K Dairy:** `tkdairy` / `password123`

## 📊 Data Flow

```
External APIs (Samsara, Milk Movement)
           ↓
    Data Population Scripts
           ↓
      PostgreSQL Database
           ↓
       FastAPI Backend
           ↓
      React Frontend
```

### Data Population Schedule

- **Tank Data:** Every 10 minutes
- **Route Data:** Every hour
- **Volume Data:** Daily (with monthly aggregation)

## 🗄️ Database Schema

### Core Tables

- `dairies` - Dairy client information
- `users` - User accounts and authentication

### Data Tables

- `tanks_data` - Real-time tank levels and status
- `routes_data` - Daily route information
- `volumes_data` - Monthly volume totals by handler

## 🔧 Development

### Running Individual Scripts

```bash
# Populate tank data
python scripts/populate_tanks_data.py

# Populate route data
python scripts/populate_routes_data.py

# Populate volume data (current month)
python scripts/populate_volumes_data.py

# Populate volume data (specific month)
python scripts/populate_volumes_data.py --year 2024 --month 11
```

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd milk-ops-insights-dashboard
npm install
npm start
```

### Testing

```bash
# Test database setup
python test_setup.py

# View logs
docker-compose logs -f backend
docker-compose logs -f scheduler
```

## 🚢 Production Deployment

### Hetzner Server Deployment

1. **Prepare the server:**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy the application:**
   ```bash
   git clone <repository>
   cd DairyMen
   
   # Update environment variables for production
   cp docker-compose.yml docker-compose.prod.yml
   # Edit docker-compose.prod.yml with production settings
   
   # Start production services
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 🔐 Security Considerations

- Change default passwords in production
- Use environment variables for sensitive configuration
- Enable SSL/TLS with Let's Encrypt
- Restrict database access to application containers only
- Regular database backups

## 📝 API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### Data Endpoints
- `GET /api/dashboard/{dairy_id}` - Dashboard summary
- `GET /api/tanks/{dairy_id}` - Tank status data
- `GET /api/routes/{dairy_id}/today` - Route information
- `GET /api/volumes/{dairy_id}` - Volume data

### Admin Endpoints
- `GET /api/admin/dairies` - All dairies (admin only)
- `GET /api/data-freshness/{dairy_id}` - Data update timestamps

## 🛠️ Troubleshooting

### Common Issues

1. **Database connection errors:**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # View database logs
   docker-compose logs postgres
   ```

2. **Data not updating:**
   ```bash
   # Check scheduler logs
   docker-compose logs scheduler
   
   # Manually run population scripts
   python scripts/populate_tanks_data.py
   ```

3. **API errors:**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Test database connection
   python test_setup.py
   ```

### Performance Monitoring

- Monitor database query performance
- Check scheduler execution logs
- Monitor API response times
- Set up alerts for data freshness

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Your License Here]

---

**Note:** This system is designed to be simple, reliable, and easy to maintain. The database-driven approach ensures fast responses and offline capability while maintaining the power of your existing data collection scripts. 