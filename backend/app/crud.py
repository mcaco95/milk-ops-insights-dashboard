from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, date, timedelta
from typing import Optional, List
import calendar

from .models import User, Dairy

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_dairy_by_id(db: Session, dairy_id: str):
    """Get dairy by ID"""
    return db.query(Dairy).filter(Dairy.id == dairy_id).first()

def get_all_dairies(db: Session):
    """Get all dairies"""
    return db.query(Dairy).filter(Dairy.active == True).all()

# ============================================================================
# TANK DATA QUERIES
# ============================================================================

def get_tanks_data(db: Session, dairy_id: str):
    """Get current tank data for a dairy"""
    query = text("""
        SELECT 
            barn_name,
            tank_name,
            current_volume_lbs,
            base_volume_lbs,
            predicted_added_lbs,
            capacity_lbs,
            time_to_full_hours,
            is_milking,
            last_pulled_at,
            wash_started_at,
            CASE 
                WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.95 THEN 'critical'
                WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.85 THEN 'warning'
                ELSE 'normal'
            END as status,
            -- Calculate fill percentage, ensuring no division by zero
            CASE
                WHEN capacity_lbs > 0 THEN ROUND(CAST((current_volume_lbs::float / capacity_lbs::float) * 100 AS numeric), 1)
                ELSE 0
            END as fill_percentage
        FROM tanks_data 
        WHERE dairy_id = :dairy_id
        ORDER BY barn_name, tank_name
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id})
    tanks = result.fetchall()

    # Calculate super loads available
    total_volume_query = text("""
        SELECT SUM(current_volume_lbs) as total_volume
        FROM tanks_data
        WHERE dairy_id = :dairy_id
    """)
    total_volume_result = db.execute(total_volume_query, {"dairy_id": dairy_id}).fetchone()
    total_volume = total_volume_result.total_volume if total_volume_result and total_volume_result.total_volume else 0
    
    SUPER_LOAD_LBS = 80000
    super_loads_available = total_volume // SUPER_LOAD_LBS

    return {
        "tanks": tanks,
        "super_loads_available": super_loads_available
    }

def get_tank_summary(db: Session, dairy_id: str):
    """Get tank summary metrics for dashboard"""
    query = text("""
        SELECT 
            COUNT(*) as total_tanks,
            COUNT(CASE WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.95 THEN 1 END) as tanks_full,
            COUNT(CASE WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.95 THEN 1 END) as critical_alerts,
            ROUND(CAST(AVG((current_volume_lbs::float / capacity_lbs::float) * 100) AS numeric), 0) as avg_capacity_utilization
        FROM tanks_data 
        WHERE dairy_id = :dairy_id
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id})
    return result.fetchone()

# ============================================================================
# ROUTES DATA QUERIES
# ============================================================================

def get_routes_data(db: Session, dairy_id: str, target_date: Optional[date] = None):
    """Get route data for a dairy and date"""
    if target_date is None:
        target_date = date.today()
    
    query = text("""
        SELECT 
            samsara_route_id,
            driver_name,
            truck_id,
            status,
            estimated_arrival,
            start_date,
            route,
            dairy_name,
            tank,
            processor,
            lt_number,
            fairlife_number,
            tracking_link,
            last_updated
        FROM routes_data 
        WHERE dairy_id = :dairy_id 
        AND report_date = :target_date
        ORDER BY start_date ASC NULLS LAST, driver_name
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id, "target_date": target_date})
    return result.fetchall()

def get_active_routes_count(db: Session, dairy_id: str):
    """Get count of active routes for dashboard"""
    query = text("""
        SELECT COUNT(*) as active_routes
        FROM routes_data 
        WHERE dairy_id = :dairy_id 
        AND report_date = :today
        AND status = 'active'
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id, "today": date.today()})
    return result.fetchone().active_routes or 0

# ============================================================================
# VOLUMES DATA QUERIES
# ============================================================================

def get_volumes_data(db: Session, dairy_id: str, month: Optional[str] = None):
    """Get volume data for a dairy and month"""
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    
    # Parse month string to date
    year, month_num = int(month[:4]), int(month[5:7])
    report_month = date(year, month_num, 1)
    
    query = text("""
        SELECT 
            handler_name,
            total_volume_lbs,
            pickup_count,
            last_updated
        FROM volumes_data 
        WHERE dairy_id = :dairy_id 
        AND report_month = :report_month
        ORDER BY total_volume_lbs DESC
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id, "report_month": report_month})
    return result.fetchall()

def get_monthly_volume_total(db: Session, dairy_id: str):
    """Get total monthly volume for dashboard"""
    current_month = date.today().replace(day=1)
    
    query = text("""
        SELECT COALESCE(SUM(total_volume_lbs), 0) as monthly_volume
        FROM volumes_data 
        WHERE dairy_id = :dairy_id 
        AND report_month = :current_month
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id, "current_month": current_month})
    return result.fetchone().monthly_volume or 0

def get_pickup_logs(db: Session, dairy_id: str, month: Optional[str] = None):
    """Get raw pickup logs for a dairy and month for CSV export."""
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    
    year, month_num = int(month[:4]), int(month[5:7])
    report_month = date(year, month_num, 1)

    query = text("""
        SELECT 
            pickup_date,
            driver_name,
            invoice_number,
            route_number,
            handler_name,
            dropoff_weight,
            trailer_number,
            truck_number
        FROM pickup_logs
        WHERE dairy_id = :dairy_id 
        AND report_month = :report_month
        ORDER BY pickup_date DESC
    """)
    
    result = db.execute(query, {"dairy_id": dairy_id, "report_month": report_month})
    return result.fetchall()

def get_volume_history(db: Session, dairy_id: str, months: int = 6):
    """Get volume history for the last N months"""
    end_date = date.today().replace(day=1)
    start_date = end_date - timedelta(days=months*31)  # Rough approximation
    
    query = text("""
        SELECT 
            report_month,
            handler_name,
            total_volume_lbs
        FROM volumes_data 
        WHERE dairy_id = :dairy_id 
        AND report_month >= :start_date
        AND report_month <= :end_date
        ORDER BY report_month DESC, handler_name
    """)
    
    result = db.execute(query, {
        "dairy_id": dairy_id, 
        "start_date": start_date, 
        "end_date": end_date
    })
    return result.fetchall()

# ============================================================================
# DASHBOARD SUMMARY QUERIES
# ============================================================================

def get_dashboard_summary(db: Session, dairy_id: str):
    """Get all dashboard summary data in one query"""
    query = text("""
        WITH tank_summary AS (
            SELECT 
                COUNT(*) as total_tanks,
                COUNT(CASE WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.95 THEN 1 END) as tanks_full,
                COUNT(CASE WHEN (current_volume_lbs::float / capacity_lbs::float) >= 0.95 THEN 1 END) as critical_alerts,
                ROUND(CAST(AVG((current_volume_lbs::float / capacity_lbs::float) * 100) AS numeric), 0) as capacity_utilization
            FROM tanks_data 
            WHERE dairy_id = :dairy_id
        ),
        active_routes AS (
            SELECT COUNT(*) as active_routes
            FROM routes_data 
            WHERE dairy_id = :dairy_id 
            AND report_date = :today
            AND status = 'active'
        ),
        monthly_volume AS (
            SELECT COALESCE(SUM(total_volume_lbs), 0) as monthly_volume
            FROM volumes_data 
            WHERE dairy_id = :dairy_id 
            AND report_month = :current_month
        )
        SELECT 
            (SELECT total_tanks FROM tank_summary) as total_tanks,
            (SELECT tanks_full FROM tank_summary) as tanks_full,
            (SELECT critical_alerts FROM tank_summary) as critical_alerts,
            (SELECT capacity_utilization FROM tank_summary) as capacity_utilization,
            (SELECT active_routes FROM active_routes) as active_routes,
            (SELECT monthly_volume FROM monthly_volume) as monthly_volume
    """)

    params = {
        "dairy_id": dairy_id,
        "today": date.today(),
        "current_month": date.today().replace(day=1)
    }
    
    result = db.execute(query, params).fetchone()
    
    return {
        "total_tanks": result.total_tanks if result else 0,
        "tanks_full": result.tanks_full if result else 0,
        "critical_alerts": result.critical_alerts if result else 0,
        "capacity_utilization": result.capacity_utilization if result else 0,
        "active_routes": result.active_routes if result else 0,
        "monthly_volume": result.monthly_volume if result else 0
    }

# ============================================================================
# DATA FRESHNESS QUERIES
# ============================================================================

def get_data_freshness(db: Session, dairy_id: str):
    """Get timestamps of last data updates"""
    queries = {
        "tanks": text("""
            SELECT MAX(last_updated) as last_update 
            FROM tanks_data 
            WHERE dairy_id = :dairy_id
        """),
        "routes": text("""
            SELECT MAX(last_updated) as last_update 
            FROM routes_data 
            WHERE dairy_id = :dairy_id 
            AND report_date = :today
        """),
        "volumes": text("""
            SELECT MAX(last_updated) as last_update 
            FROM volumes_data 
            WHERE dairy_id = :dairy_id
        """)
    }
    
    freshness = {}
    for data_type, query in queries.items():
        params = {"dairy_id": dairy_id}
        if data_type == "routes":
            params["today"] = date.today()
            
        result = db.execute(query, params)
        row = result.fetchone()
        freshness[data_type] = row.last_update if row and row.last_update else None
    
    return freshness 