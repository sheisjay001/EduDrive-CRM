"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel } from "@/components/dashboard/ops-primitives";
import { Bus, MapPin, User, Clock, AlertCircle } from "lucide-react";
import { getAccessToken, getUser } from "@/services/auth-storage";

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
  stops?: Array<{ id: string; name: string; pickup_time?: string }>;
}

interface ChildRoute {
  child_name?: string;
  route_name?: string;
  stop_name?: string;
  pickup_time?: string;
}

export default function ParentBusRoutesPage() {
  const [loading, setLoading] = useState(true);
  const [routes, setRoutes] = useState<BusRoute[]>([]);
  const [childRoute, setChildRoute] = useState<ChildRoute | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
    
    Promise.allSettled([
      fetch(`${API_URL}/bus-routes`, { headers }).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/parent/transport`, { headers }).then(r => r.ok ? r.json() : null),
    ]).then(([rRes, tRes]) => {
      if (rRes.status === "fulfilled" && rRes.value) setRoutes(Array.isArray(rRes.value) ? rRes.value : rRes.value.routes || []);
      if (tRes.status === "fulfilled" && tRes.value) setChildRoute(tRes.value);
    }).catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell
      eyebrow="Parent Portal"
      title="Transportation"
      description="View your child's bus route, pickup times, and transportation information."
      allowedRoles={["parent"]}
    >
      {loading ? (
        <LoadingPanel />
      ) : error ? (
        <Card className="p-6 text-center text-red-400">{error}</Card>
      ) : (
        <div className="space-y-6">
          {childRoute ? (
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Your Child's Transportation</h3>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-[#9eb1cf]">Child</p>
                  <p className="mt-2 text-lg font-semibold text-white">{childRoute.child_name || "Unknown"}</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-wider text-[#9eb1cf]">Route</p>
                  <p className="mt-2 text-lg font-semibold text-white">{childRoute.route_name || "Not assigned"}</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <MapPin className="h-4 w-4 text-[#d9a441]" />
                    <p className="text-xs uppercase tracking-wider text-[#9eb1cf]">Pickup Stop</p>
                  </div>
                  <p className="text-lg font-semibold text-white">{childRoute.stop_name || "Not assigned"}</p>
                </div>
                <div className="rounded-xl border border-white/10 bg-white/5 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 text-[#d9a441]" />
                    <p className="text-xs uppercase tracking-wider text-[#9eb1cf]">Pickup Time</p>
                  </div>
                  <p className="text-lg font-semibold text-white">{childRoute.pickup_time || "Not specified"}</p>
                </div>
              </div>
            </Card>
          ) : (
            <Card className="p-12 text-center">
              <Bus className="h-16 w-16 mx-auto text-[#9eb1cf] mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Transportation Assigned</h3>
              <p className="text-[#9eb1cf]">Your child is not currently assigned to a bus route. Please contact the school administration.</p>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Available Bus Routes</h3>
            {routes.length === 0 ? (
              <p className="text-[#9eb1cf]">No bus routes configured.</p>
            ) : (
              <div className="space-y-4">
                {routes.map((route) => (
                  <div key={route.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20 text-[#d9a441]">
                          <Bus className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-white">{route.name || route.route_name}</h4>
                          <p className="text-sm text-[#9eb1cf]">Code: {route.route_code}</p>
                        </div>
                      </div>
                      <Badge tone={route.status === "active" ? "good" : "neutral"}>
                        {route.status || "active"}
                      </Badge>
                    </div>
                    <div className="grid gap-3 md:grid-cols-3 mt-4 text-sm text-[#9eb1cf]">
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        Driver: {route.driver_name || "Not assigned"}
                      </div>
                      <div className="flex items-center gap-2">
                        <Bus className="h-4 w-4" />
                        Vehicle: {route.vehicle_number || "Not assigned"}
                      </div>
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        {route.stop_count || 0} stops
                      </div>
                    </div>
                    {route.stops && route.stops.length > 0 && (
                      <div className="mt-4">
                        <p className="text-xs uppercase tracking-wider text-[#8ea4c8] mb-2">Route Stops</p>
                        <div className="flex flex-wrap gap-2">
                          {route.stops.map((stop) => (
                            <Badge key={stop.id} className="border-white/20 text-white">
                              {stop.name}
                              {stop.pickup_time && ` (${stop.pickup_time})`}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>

          <Card className="p-6 border-[#d9a441]/30">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-[#d9a441] mt-0.5" />
              <div>
                <h4 className="font-semibold text-white">Transportation Changes</h4>
                <p className="mt-1 text-sm text-[#c9d7ef]">
                  If you need to change your child's bus route or pickup location, please contact the school administration at least 48 hours in advance.
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
