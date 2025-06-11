from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Optional
import logging

from .database import get_db
from .models import User, Dairy
from .schemas import LoginRequest, LoginResponse, DashboardResponse, VolumesResponse, RoutesResponse, TanksResponse, AdminDairiesResponse, DairyInfo, VolumeData, RouteData, TankData, PickupLogsResponse
from .auth import verify_password, create_access_token, decode_token
from .crud import (
    get_user_by_username, 
    get_dairy_by_id, 
    get_all_dairies,
    get_dashboard_summary,
    get_tanks_data,
    get_routes_data,
    get_volumes_data,
    get_pickup_logs,
    get_data_freshness
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dairy Operations API", version="2.0.0", description="Simplified database-driven API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Verify JWT token and return current user"""
    try:
        payload = decode_token(credentials.credentials)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Handle admin user
        if username == "admin" and payload.get("is_admin"):
            class AdminUser:
                def __init__(self):
                    self.username = "admin"
                    self.id = -1
                    self.is_admin = True
                    self.dairy_id = None
            return AdminUser()
        
        user = get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    
    # Check for admin login
    if credentials.username == "admin" and credentials.password == "admin123":
        access_token = create_access_token(data={"sub": "admin", "is_admin": True})
        logger.info("Admin user logged in")
        return LoginResponse(
            token=access_token,
            dairy_name="Admin Dashboard",
            dairy_id="admin",
            expires_in=86400,
            is_admin=True
        )
    
    user = get_user_by_username(db, credentials.username)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Get dairy information
    dairy = get_dairy_by_id(db, user.dairy_id)
    if not dairy:
        raise HTTPException(status_code=404, detail="Dairy not found")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    logger.info(f"User {user.username} logged in for dairy {dairy.name}")
    
    return LoginResponse(
        token=access_token,
        dairy_name=dairy.name,
        dairy_id=dairy.id,
        expires_in=86400
    )

@app.get("/api/dashboard/{dairy_id}", response_model=DashboardResponse)
async def get_dashboard(
    dairy_id: str, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get dashboard summary data from database"""
    # Allow admin access to any dairy, otherwise verify user has access to this dairy
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Verify dairy exists
        dairy = get_dairy_by_id(db, dairy_id)
        if not dairy:
            raise HTTPException(status_code=404, detail="Dairy not found")
        
        # Get dashboard summary from database
        summary = get_dashboard_summary(db, dairy_id)
        
        logger.info(f"Dashboard data served for dairy {dairy_id}")
        return DashboardResponse(**summary)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

@app.get("/api/volumes/{dairy_id}", response_model=VolumesResponse)
async def get_volumes(
    dairy_id: str,
    month: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly volumes data from database"""
    # Allow admin access to any dairy, otherwise verify user has access to this dairy
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    try:
        # Verify dairy exists
        dairy = get_dairy_by_id(db, dairy_id)
        if not dairy:
            raise HTTPException(status_code=404, detail="Dairy not found")
        
        # Get volumes data from database
        volumes_data = get_volumes_data(db, dairy_id, month)
        
        # Convert to response format
        volume_entries = []
        total_volume = 0
        total_pickup_count = 0
        
        for row in volumes_data:
            # Create a simplified entry per handler
            volume_entries.append(VolumeData(
                date=f"{month}-01",  # First day of month
                volume=row.total_volume_lbs,
                pickup_count=row.pickup_count,
                customer=row.handler_name
            ))
            total_volume += row.total_volume_lbs
            total_pickup_count += row.pickup_count
        
        logger.info(f"Volumes data served for dairy {dairy_id}, month {month}")
        return VolumesResponse(
            month=month,
            total_volume=total_volume,
            total_pickup_count=total_pickup_count,
            volumes=volume_entries
        )
        
    except Exception as e:
        logger.error(f"Error fetching volumes data for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching volumes data: {str(e)}")

@app.get("/api/pickup-logs/{dairy_id}", response_model=PickupLogsResponse, summary="Get Raw Pickup Logs for CSV Export")
async def get_pickup_logs_endpoint(
    dairy_id: str,
    month: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches the raw, individual pickup records for a specific dairy and month.
    This endpoint is designed to provide the data needed for the detailed CSV export.
    """
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        logs = get_pickup_logs(db, dairy_id, month)
        return PickupLogsResponse(logs=logs)
    except Exception as e:
        logger.error(f"Error fetching pickup logs for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching pickup logs: {str(e)}")

@app.get("/api/routes/{dairy_id}/today", response_model=RoutesResponse)
async def get_routes(
    dairy_id: str,
    target_date: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get routes data from database"""
    # Allow admin access to any dairy, otherwise verify user has access to this dairy
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Parse target date
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        else:
            parsed_date = date.today()
        
        # Verify dairy exists
        dairy = get_dairy_by_id(db, dairy_id)
        if not dairy:
            raise HTTPException(status_code=404, detail="Dairy not found")
        
        # Get routes data from database
        routes_data = get_routes_data(db, dairy_id, parsed_date)
        
        # Convert to response format
        route_entries = []
        for i, row in enumerate(routes_data):
            route_entries.append(RouteData(
                id=str(row.id),  # Use actual UUID
                dairy_id=row.dairy_id,
                samsara_route_id=row.samsara_route_id,
                samsara_route_name=getattr(row, 'samsara_route_name', None),  # ENHANCED: Full route name
                report_date=row.report_date,
                driver_name=row.driver_name,
                truck_id=row.truck_id,
                status=row.status,
                
                # ENHANCED: Separate timestamp fields
                depot_departure_time=getattr(row, 'depot_departure_time', None),
                dairy_arrival_time=getattr(row, 'dairy_arrival_time', None),
                dairy_departure_time=getattr(row, 'dairy_departure_time', None),
                estimated_eta=getattr(row, 'estimated_eta', None),
                
                # Legacy fields (for backwards compatibility)
                estimated_arrival=row.estimated_arrival,
                start_date=row.start_date,
                
                route=row.route,
                dairy_name=row.dairy_name,
                tank=row.tank,
                samsara_tank=row.samsara_tank,  # Tank info from Samsara
                processor=row.processor,
                lt_number=row.lt_number,
                fairlife_number=row.fairlife_number,
                tracking_link=row.tracking_link,
                last_updated=row.last_updated
            ))
        
        logger.info(f"Routes data served for dairy {dairy_id}, date {parsed_date}")
        return RoutesResponse(
            date=parsed_date.strftime("%Y-%m-%d"),
            routes=route_entries
        )
        
    except Exception as e:
        logger.error(f"Error fetching routes data for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching routes data: {str(e)}")

@app.get("/api/tanks/{dairy_id}", response_model=TanksResponse)
async def get_tanks(
    dairy_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tank status data from database"""
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        dairy = get_dairy_by_id(db, dairy_id)
        if not dairy:
            raise HTTPException(status_code=404, detail="Dairy not found")
        
        # Get tanks data and super loads calculation from the updated CRUD function
        tanks_result = get_tanks_data(db, dairy_id)
        
        tank_entries = [TankData.from_orm(row) for row in tanks_result["tanks"]]
        
        logger.info(f"Tanks data served for dairy {dairy_id}")
        return TanksResponse(
            dairy_id=dairy_id,
            tanks=tank_entries,
            super_loads_available=tanks_result["super_loads_available"]
        )
        
    except Exception as e:
        logger.error(f"Error fetching tanks data for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching tanks data: {str(e)}")

@app.get("/api/admin/dairies", response_model=AdminDairiesResponse)
async def get_all_dairies_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all dairies (admin only)"""
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        dairies = get_all_dairies(db)
        dairy_info = []
        
        for dairy in dairies:
            dairy_info.append(DairyInfo(
                id=dairy.id,
                name=dairy.name,
                active=dairy.active
            ))
        
        return AdminDairiesResponse(dairies=dairy_info)
        
    except Exception as e:
        logger.error(f"Error fetching dairies data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching dairies data: {str(e)}")

@app.get("/api/data-freshness/{dairy_id}")
async def get_data_freshness_endpoint(
    dairy_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data freshness information"""
    # Allow admin access to any dairy, otherwise verify user has access to this dairy
    if not hasattr(user, 'is_admin') and user.dairy_id != dairy_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        freshness = get_data_freshness(db, dairy_id)
        
        # Convert timestamps to ISO format
        for key, value in freshness.items():
            if value:
                freshness[key] = value.isoformat()
        
        return freshness
        
    except Exception as e:
        logger.error(f"Error fetching data freshness for dairy {dairy_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data freshness: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "database_driven": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 