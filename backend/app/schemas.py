from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    dairy_name: str
    dairy_id: str
    expires_in: int
    is_admin: Optional[bool] = False

class DairyInfo(BaseModel):
    id: str
    name: str
    active: bool

class AdminDairiesResponse(BaseModel):
    dairies: List[DairyInfo]

# Dashboard schemas
class DashboardResponse(BaseModel):
    total_tanks: int
    tanks_full: int
    active_routes: int
    monthly_volume: int
    capacity_utilization: int
    critical_alerts: int

# Volumes schemas
class VolumeData(BaseModel):
    date: str
    volume: int
    pickup_count: int
    customer: str

class VolumesResponse(BaseModel):
    month: str
    total_volume: int
    total_pickup_count: int
    volumes: List[VolumeData]

# Pickup Logs Schemas (for CSV export)
class PickupLogData(BaseModel):
    pickup_date: Optional[datetime] = None
    driver_name: Optional[str] = None
    invoice_number: Optional[str] = None
    route_number: Optional[str] = None
    handler_name: Optional[str] = None
    dropoff_weight: Optional[int] = None
    trailer_number: Optional[str] = None
    truck_number: Optional[str] = None

    class Config:
        from_attributes = True

class PickupLogsResponse(BaseModel):
    logs: List[PickupLogData]

# Routes schemas
class CurrentLocation(BaseModel):
    lat: float
    lng: float

class RouteData(BaseModel):
    id: int
    route_number: str
    driver_name: Optional[str] = None
    truck_id: Optional[str] = None
    status: str
    estimated_arrival: str
    start_date: Optional[str] = None
    route: Optional[str] = None
    dairy_name: Optional[str] = None
    tank: Optional[str] = None
    processor: Optional[str] = None
    lt_number: Optional[str] = None
    fairlife_number: Optional[str] = None
    tracking_link: Optional[str] = None

    class Config:
        from_attributes = True

class RoutesResponse(BaseModel):
    date: str
    routes: List[RouteData]

# Tanks schemas
class TankData(BaseModel):
    barn_name: Optional[str] = None
    tank_name: str
    
    # Volume and Capacity
    current_volume_lbs: int
    base_volume_lbs: Optional[int] = None
    predicted_added_lbs: Optional[int] = None
    capacity_lbs: int
    fill_percentage: float
    time_to_full_hours: Optional[float] = None
    
    # Status and Timestamps
    status: str  # 'normal' | 'warning' | 'critical' | 'washing'
    is_milking: bool
    last_pulled_at: Optional[datetime] = None
    wash_started_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TanksResponse(BaseModel):
    dairy_id: str
    tanks: List[TankData]
    super_loads_available: int 