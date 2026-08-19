"use client";

import { useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { MapPin, User, Bus, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface BusRoute {
  id: string;
  route_name: string;
  route_code: string;
  name?: string;
  status?: string;
  capacity: number;
  stop_count?: number;
  driver_name?: string;
  vehicle_number?: string;
  stops?: Array<{ id: string; name: string }>;
}

interface BusStop {
  id: string;
  stop_name: string;
  location: string;
  route_id: string;
}

export default function BusRoutesPage() {
  const [routes, setRoutes] = useState<BusRoute[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateRouteDialog, setShowCreateRouteDialog] = useState(false);
  const [showCreateStopDialog, setShowCreateStopDialog] = useState(false);

  const fetchBusRoutes = async () => {
    try {
      const response = await fetch(`${API_URL}/bus-routes`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRoutes(Array.isArray(data) ? data : data.routes || []);
      }
    } catch (error) {
      console.error("Error fetching bus routes:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useState(() => {
    fetchBusRoutes();
  });

  const handleCreateRoute = async (routeData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/bus-routes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(routeData),
      });

      if (response.ok) {
        setShowCreateRouteDialog(false);
        fetchBusRoutes();
      }
    } catch (error) {
      console.error("Error creating bus route:", error);
    }
  };

  const handleCreateStop = async (stopData: Record<string, unknown>) => {
    try {
      const response = await fetch(`${API_URL}/bus-stops`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify(stopData),
      });

      if (response.ok) {
        setShowCreateStopDialog(false);
        fetchBusRoutes();
      }
    } catch (error) {
      console.error("Error creating bus stop:", error);
    }
  };

  return (
    <AppShell
      eyebrow="Bus Routes Management"
      title="Transportation system configuration"
      description="Manage bus routes, stops, drivers, and student assignments for school transportation services."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button variant="secondary">
                <Bus className="mr-2 h-4 w-4" />
                Routes ({routes.length})
              </Button>
              <Button variant="secondary">
                <MapPin className="mr-2 h-4 w-4" />
                Stops ({routes.reduce((acc, route) => acc + (route.stops?.length || 0), 0)})
              </Button>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setShowCreateStopDialog(true)}>
                <MapPin className="mr-2 h-4 w-4" />
                Add Stop
              </Button>
              <Button onClick={() => setShowCreateRouteDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Route
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            {routes.length === 0 ? (
              <Card className="p-6">
                <p className="text-center text-[#9eb1cf]">No bus routes configured</p>
              </Card>
            ) : (
              routes.map((route) => (
                <Card key={route.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-white">{route.name}</h3>
                        <Badge className="border-[#d9a441]/30 text-[#d9a441]">
                          {route.status || 'active'}
                        </Badge>
                      </div>
                      <div className="mt-3 flex items-center gap-4 text-sm text-[#9eb1cf]">
                        <span className="flex items-center gap-2">
                          <User className="h-4 w-4" />
                          Driver: {route.driver_name || 'Not assigned'}
                        </span>
                        <span className="flex items-center gap-2">
                          <Bus className="h-4 w-4" />
                          Vehicle: {route.vehicle_number || 'Not assigned'}
                        </span>
                        <span className="flex items-center gap-2">
                          <MapPin className="h-4 w-4" />
                          {route.stop_count || 0} stops
                        </span>
                      </div>
                      <div className="mt-4">
                        <p className="text-xs uppercase tracking-[0.25em] text-[#8ea4c8]">Route Stops</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {route.stops?.map((stop) => (
                            <Badge key={stop.id} className="border-white/20 text-white">
                              {stop.name}
                            </Badge>
                          )) || <span className="text-sm text-[#9eb1cf]">No stops configured</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                        Edit
                      </Button>
                      <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                        Delete
                      </Button>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}
