from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.core.auth import get_current_user, AuthUser, has_permission
from app.database.session import get_supabase_client

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
    supabase = get_supabase_client()
    try:
        result = supabase.table("bus_routes").select("*").order("route_name").execute()
        routes = result.data or []
        for route in routes:
            stops_res = supabase.table("bus_stops").select("*").eq("route_id", route["id"]).order("stop_order").execute()
            route["stops"] = stops_res.data or []
            route["stop_count"] = len(route["stops"])
            route["name"] = route.get("route_name") or route.get("name")
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bus-routes/{route_id}")
async def get_bus_route(
    route_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    supabase = get_supabase_client()
    try:
        result = supabase.table("bus_routes").select("*").eq("id", route_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Bus route not found")
        route = result.data[0]
        stops_res = supabase.table("bus_stops").select("*").eq("route_id", route_id).order("stop_order").execute()
        route["stops"] = stops_res.data or []
        route["stop_count"] = len(route["stops"])
        route["name"] = route.get("route_name") or route.get("name")
        return route
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bus-routes")
async def create_bus_route(
    payload: BusRouteCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    supabase = get_supabase_client()
    try:
        row = {
            "route_name": payload.route_name,
            "route_code": payload.route_code,
            "capacity": payload.capacity,
            "driver_name": payload.driver_name,
            "vehicle_number": payload.vehicle_number,
            "status": payload.status,
        }
        if current_user.school_id:
            row["school_id"] = current_user.school_id
        result = supabase.table("bus_routes").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bus-routes/{route_id}")
async def update_bus_route(
    route_id: str,
    payload: BusRouteUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    supabase = get_supabase_client()
    try:
        existing = supabase.table("bus_routes").select("id").eq("id", route_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Bus route not found")
        changes = payload.model_dump(exclude_none=True)
        result = supabase.table("bus_routes").update(changes).eq("id", route_id).execute()
        return result.data[0] if result.data else {"id": route_id, **changes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bus-routes/{route_id}")
async def delete_bus_route(
    route_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    supabase = get_supabase_client()
    try:
        supabase.table("student_transport").delete().eq("route_id", route_id).execute()
        supabase.table("bus_stops").delete().eq("route_id", route_id).execute()
        supabase.table("bus_routes").delete().eq("id", route_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- Bus Stops -------------------

@router.get("/bus-stops")
async def list_bus_stops(
    route_id: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    supabase = get_supabase_client()
    try:
        query = supabase.table("bus_stops").select("*")
        if route_id:
            query = query.eq("route_id", route_id)
        result = query.order("stop_order").execute()
        return result.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bus-stops")
async def create_bus_stop(
    payload: BusStopCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    supabase = get_supabase_client()
    try:
        row = {
            "route_id": payload.route_id,
            "stop_name": payload.stop_name,
            "location": payload.location,
            "stop_order": payload.stop_order,
        }
        if current_user.school_id:
            row["school_id"] = current_user.school_id
        result = supabase.table("bus_stops").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bus-stops/{stop_id}")
async def update_bus_stop(
    stop_id: str,
    payload: BusStopUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    supabase = get_supabase_client()
    try:
        existing = supabase.table("bus_stops").select("id").eq("id", stop_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Bus stop not found")
        changes = payload.model_dump(exclude_none=True)
        result = supabase.table("bus_stops").update(changes).eq("id", stop_id).execute()
        return result.data[0] if result.data else {"id": stop_id, **changes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bus-stops/{stop_id}")
async def delete_bus_stop(
    stop_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    supabase = get_supabase_client()
    try:
        supabase.table("bus_stops").delete().eq("id", stop_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- Student Transport Assignment -------------------

@router.get("/students")
async def list_student_transport(
    route_id: Optional[str] = None,
    student_id: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    supabase = get_supabase_client()
    try:
        query = supabase.table("student_transport").select("*, students(*)")
        if route_id:
            query = query.eq("route_id", route_id)
        if student_id:
            query = query.eq("student_id", student_id)
        if current_user.role == "parent" and current_user.id:
            families = supabase.table("families").select("*").eq("primary_contact_id", current_user.id).execute()
            family_ids = [f["id"] for f in (families.data or [])]
            students = supabase.table("students").select("*").in_("family_id", family_ids).execute()
            student_ids = [s["id"] for s in (students.data or [])]
            if student_id:
                if student_id not in student_ids:
                    return []
            else:
                query = query.in_("student_id", student_ids)
        result = query.execute()
        return result.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/students")
async def assign_student_transport(
    payload: StudentTransportAssign,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    supabase = get_supabase_client()
    try:
        existing = supabase.table("student_transport").select("*").eq("student_id", payload.student_id).execute()
        row = {
            "student_id": payload.student_id,
            "route_id": payload.route_id,
            "stop_id": payload.stop_id,
            "pickup_location": payload.pickup_location,
            "dropoff_location": payload.dropoff_location,
            "status": "active",
        }
        if current_user.school_id:
            row["school_id"] = current_user.school_id
        if existing.data:
            result = supabase.table("student_transport").update(row).eq("student_id", payload.student_id).execute()
        else:
            result = supabase.table("student_transport").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/students/{student_id}")
async def unassign_student_transport(
    student_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    supabase = get_supabase_client()
    try:
        supabase.table("student_transport").delete().eq("student_id", student_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- Vehicles & Tracking -------------------

@router.get("/vehicles")
async def list_vehicles(
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "view")
    supabase = get_supabase_client()
    try:
        result = supabase.table("vehicles").select("*").order("vehicle_number").execute()
        return result.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vehicles")
async def create_vehicle(
    payload: VehicleCreate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "create")
    supabase = get_supabase_client()
    try:
        row = {
            "vehicle_number": payload.vehicle_number,
            "vehicle_type": payload.vehicle_type,
            "capacity": payload.capacity,
            "driver_name": payload.driver_name,
            "driver_phone": payload.driver_phone,
            "status": "active",
        }
        if current_user.school_id:
            row["school_id"] = current_user.school_id
        result = supabase.table("vehicles").insert(row).execute()
        return result.data[0] if result.data else row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdate,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "edit")
    supabase = get_supabase_client()
    try:
        existing = supabase.table("vehicles").select("id").eq("id", vehicle_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        changes = payload.model_dump(exclude_none=True)
        if "last_known_lat" in changes or "last_known_lng" in changes:
            changes["last_updated"] = datetime.utcnow().isoformat()
        result = supabase.table("vehicles").update(changes).eq("id", vehicle_id).execute()
        return result.data[0] if result.data else {"id": vehicle_id, **changes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    _enforce_transport_perm(current_user, "delete")
    supabase = get_supabase_client()
    try:
        supabase.table("vehicles").delete().eq("id", vehicle_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
