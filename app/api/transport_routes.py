from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser, has_permission
from app.database.session import get_db
import uuid

router = APIRouter(prefix="/transport", tags=["transport"])
compat_router = APIRouter(tags=["transport"])


class BusRouteCreate(BaseModel):
    route_name: str
    route_code: str
    capacity: int = 0
    driver_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    status: str = "active"


class BusRouteUpdate(BaseModel):
    route_name: Optional[str] = None
    route_code: Optional[str] = None
    capacity: Optional[int] = None
    driver_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    status: Optional[str] = None


class BusStopCreate(BaseModel):
    route_id: str
    stop_name: str
    location: Optional[str] = None
    stop_order: int = 0


class BusStopUpdate(BaseModel):
    route_id: Optional[str] = None
    stop_name: Optional[str] = None
    location: Optional[str] = None
    stop_order: Optional[int] = None


class StudentTransportAssign(BaseModel):
    student_id: str
    route_id: str
    stop_id: Optional[str] = None
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None


class VehicleCreate(BaseModel):
    vehicle_number: str
    vehicle_type: Optional[str] = None
    capacity: int = 0
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class VehicleUpdate(BaseModel):
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    status: Optional[str] = None
    last_known_lat: Optional[float] = None
    last_known_lng: Optional[float] = None


def _enforce_transport_perm(current_user: AuthUser, action: str = "view"):
    role = current_user.role
    if role in ("super_admin", "school_admin", "staff"):
        return
    if role == "parent" and action in ("view", "view-own"):
        return
    if not has_permission(current_user, f"transport:{action}"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


# ------------------- Bus Routes -------------------

@router.get("/bus-routes")
async def list_bus_routes(
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM bus_routes WHERE school_id = %s ORDER BY route_name", (current_user.schoolId,))
        routes = cursor.fetchall()
        
        for route in routes:
            cursor.execute("SELECT * FROM bus_stops WHERE route_id = %s ORDER BY stop_order", (route['id'],))
            route["stops"] = cursor.fetchall()
            route["stop_count"] = len(route["stops"])
            route["name"] = route.get("route_name") or route.get("name")
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.get("/bus-routes/{route_id}")
async def get_bus_route(
    route_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM bus_routes WHERE id = %s AND school_id = %s", (route_id, current_user.schoolId))
        route = cursor.fetchone()
        
        if not route:
            raise HTTPException(status_code=404, detail="Bus route not found")
        
        cursor.execute("SELECT * FROM bus_stops WHERE route_id = %s ORDER BY stop_order", (route_id,))
        route["stops"] = cursor.fetchall()
        route["stop_count"] = len(route["stops"])
        route["name"] = route.get("route_name") or route.get("name")
        return route
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.post("/bus-routes")
async def create_bus_route(
    payload: BusRouteCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    db = get_db()
    cursor = db.cursor()
    try:
        route_id = str(uuid.uuid4())
        query = """
            INSERT INTO bus_routes (id, school_id, route_name, route_code, capacity, driver_name, vehicle_number, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            route_id,
            current_user.schoolId,
            payload.route_name,
            payload.route_code,
            payload.capacity,
            payload.driver_name,
            payload.vehicle_number,
            payload.status
        ))
        db.commit()
        return {"id": route_id, "route_name": payload.route_name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.put("/bus-routes/{route_id}")
async def update_bus_route(
    route_id: str,
    payload: BusRouteUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    db = get_db()
    cursor = db.cursor()
    try:
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join([f"{k} = %s" for k in changes.keys()])
        values = list(changes.values()) + [route_id, current_user.schoolId]
        
        query = f"UPDATE bus_routes SET {set_clause}, updated_at = NOW() WHERE id = %s AND school_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Bus route not found")
        
        db.commit()
        return {"id": route_id, **changes}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.delete("/bus-routes/{route_id}")
async def delete_bus_route(
    route_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    db = get_db()
    cursor = db.cursor()
    try:
        # Delete related records first
        cursor.execute("DELETE FROM student_transport WHERE route_id = %s", (route_id,))
        cursor.execute("DELETE FROM bus_stops WHERE route_id = %s", (route_id,))
        cursor.execute("DELETE FROM bus_routes WHERE id = %s AND school_id = %s", (route_id, current_user.schoolId))
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# ------------------- Bus Stops -------------------

@router.get("/bus-stops")
async def list_bus_stops(
    route_id: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    db = get_db()
    cursor = db.cursor()
    try:
        if route_id:
            cursor.execute("SELECT * FROM bus_stops WHERE route_id = %s AND school_id = %s ORDER BY stop_order", (route_id, current_user.schoolId))
        else:
            cursor.execute("SELECT * FROM bus_stops WHERE school_id = %s ORDER BY stop_order", (current_user.schoolId,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.post("/bus-stops")
async def create_bus_stop(
    payload: BusStopCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    db = get_db()
    cursor = db.cursor()
    try:
        stop_id = str(uuid.uuid4())
        query = """
            INSERT INTO bus_stops (id, school_id, route_id, stop_name, location, stop_order, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            stop_id,
            current_user.schoolId,
            payload.route_id,
            payload.stop_name,
            payload.location,
            payload.stop_order
        ))
        db.commit()
        return {"id": stop_id, "stop_name": payload.stop_name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.put("/bus-stops/{stop_id}")
async def update_bus_stop(
    stop_id: str,
    payload: BusStopUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    db = get_db()
    cursor = db.cursor()
    try:
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join([f"{k} = %s" for k in changes.keys()])
        values = list(changes.values()) + [stop_id, current_user.schoolId]
        
        query = f"UPDATE bus_stops SET {set_clause}, updated_at = NOW() WHERE id = %s AND school_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Bus stop not found")
        
        db.commit()
        return {"id": stop_id, **changes}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.delete("/bus-stops/{stop_id}")
async def delete_bus_stop(
    stop_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    db = get_db()
    cursor = db.cursor()
    try:
        query = "DELETE FROM bus_stops WHERE id = %s AND school_id = %s"
        cursor.execute(query, (stop_id, current_user.schoolId))
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# ------------------- Student Transport Assignment -------------------

@router.get("/students")
async def list_student_transport(
    route_id: Optional[str] = None,
    student_id: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    db = get_db()
    cursor = db.cursor()
    try:
        if route_id:
            cursor.execute("SELECT * FROM student_transport WHERE route_id = %s AND school_id = %s", (route_id, current_user.schoolId))
        elif student_id:
            cursor.execute("SELECT * FROM student_transport WHERE student_id = %s AND school_id = %s", (student_id, current_user.schoolId))
        else:
            cursor.execute("SELECT * FROM student_transport WHERE school_id = %s", (current_user.schoolId,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.post("/students")
async def assign_student_transport(
    payload: StudentTransportAssign,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM student_transport WHERE student_id = %s", (payload.student_id,))
        existing = cursor.fetchone()
        
        if existing:
            query = """
                UPDATE student_transport SET route_id = %s, stop_id = %s, pickup_location = %s, dropoff_location = %s, updated_at = NOW()
                WHERE student_id = %s
            """
            cursor.execute(query, (payload.route_id, payload.stop_id, payload.pickup_location, payload.dropoff_location, payload.student_id))
        else:
            transport_id = str(uuid.uuid4())
            query = """
                INSERT INTO student_transport (id, school_id, student_id, route_id, stop_id, pickup_location, dropoff_location, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (transport_id, current_user.schoolId, payload.student_id, payload.route_id, payload.stop_id, payload.pickup_location, payload.dropoff_location, 'active'))
        
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.delete("/students/{student_id}")
async def unassign_student_transport(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM student_transport WHERE student_id = %s", (student_id,))
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


# ------------------- Vehicles & Tracking -------------------

@router.get("/vehicles")
async def list_vehicles(
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM vehicles WHERE school_id = %s ORDER BY vehicle_number", (current_user.schoolId,))
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.post("/vehicles")
async def create_vehicle(
    payload: VehicleCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    db = get_db()
    cursor = db.cursor()
    try:
        vehicle_id = str(uuid.uuid4())
        query = """
            INSERT INTO vehicles (id, school_id, vehicle_number, vehicle_type, capacity, driver_name, driver_phone, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            vehicle_id,
            current_user.schoolId,
            payload.vehicle_number,
            payload.vehicle_type,
            payload.capacity,
            payload.driver_name,
            payload.driver_phone,
            'active'
        ))
        db.commit()
        return {"id": vehicle_id, "vehicle_number": payload.vehicle_number}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.put("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    db = get_db()
    cursor = db.cursor()
    try:
        changes = payload.model_dump(exclude_none=True)
        if not changes:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clause = ", ".join([f"{k} = %s" for k in changes.keys()])
        values = list(changes.values()) + [vehicle_id, current_user.schoolId]
        
        query = f"UPDATE vehicles SET {set_clause}, updated_at = NOW() WHERE id = %s AND school_id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        db.commit()
        return {"id": vehicle_id, **changes}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM vehicles WHERE id = %s AND school_id = %s", (vehicle_id, current_user.schoolId))
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()


compat_router.add_api_route(
    "/bus-routes", list_bus_routes, methods=["GET"]
)
compat_router.add_api_route(
    "/bus-routes/{route_id}", get_bus_route, methods=["GET"]
)
compat_router.add_api_route(
    "/bus-routes", create_bus_route, methods=["POST"]
)
compat_router.add_api_route(
    "/bus-routes/{route_id}", update_bus_route, methods=["PUT"]
)
compat_router.add_api_route(
    "/bus-routes/{route_id}", delete_bus_route, methods=["DELETE"]
)
compat_router.add_api_route(
    "/bus-stops", list_bus_stops, methods=["GET"]
)
compat_router.add_api_route(
    "/bus-stops", create_bus_stop, methods=["POST"]
)
compat_router.add_api_route(
    "/bus-stops/{stop_id}", update_bus_stop, methods=["PUT"]
)
compat_router.add_api_route(
    "/bus-stops/{stop_id}", delete_bus_stop, methods=["DELETE"]
)
