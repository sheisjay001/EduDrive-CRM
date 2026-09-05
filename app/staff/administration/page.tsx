"use client";

import { useState, useEffect } from "react";
import { AppShell } from "@/components/shell/app-shell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingPanel, SectionTitle } from "@/components/dashboard/ops-primitives";
import { Plus, User, Shield, Key } from "lucide-react";
import { getAccessToken } from "@/services/auth-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1";

interface User {
  id: string;
  full_name: string;
  email: string;
  role: string;
  status: string;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  user_name?: string;
  email?: string;
  permissions?: string[];
  user_id?: string;
}

interface RoleMatrix {
  roles: Array<{ name: string; permissions: string[] }>;
}

export default function UserAdministrationPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [roleMatrix, setRoleMatrix] = useState<RoleMatrix | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"users" | "permissions" | "roles">("users");
  const [showCreateUserDialog, setShowCreateUserDialog] = useState(false);

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/staff/overview`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(Array.isArray(data) ? data : data.staff || []);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const response = await fetch(`${API_URL}/user-admin/permissions/summary`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPermissions(Array.isArray(data) ? data : data.permissions || []);
      }
    } catch (error) {
      console.error("Error fetching permissions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRoleMatrix = async () => {
    try {
      const response = await fetch(`${API_URL}/user-admin/role-matrix`, {
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRoleMatrix(data);
      }
    } catch (error) {
      console.error("Error fetching role matrix:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      if (activeTab === "users") await fetchUsers();
      else if (activeTab === "permissions") await fetchPermissions();
      else if (activeTab === "roles") await fetchRoleMatrix();
    };
    loadData();
  }, [activeTab]);

  const handleGrantPermission = async (userId: string, permission: string) => {
    try {
      const response = await fetch(`${API_URL}/user-admin/permissions/grant`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify({ user_id: userId, permission_name: permission, action: "grant" }),
      });

      if (response.ok) {
        fetchPermissions();
      }
    } catch (error) {
      console.error("Error granting permission:", error);
    }
  };

  const handleRevokePermission = async (userId: string, permission: string) => {
    try {
      const response = await fetch(`${API_URL}/user-admin/permissions/revoke`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAccessToken()}`,
        },
        body: JSON.stringify({ user_id: userId, permission_name: permission, action: "revoke" }),
      });

      if (response.ok) {
        fetchPermissions();
      }
    } catch (error) {
      console.error("Error revoking permission:", error);
    }
  };

  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      super_admin: "bg-purple-500/20 text-purple-400",
      school_admin: "bg-blue-500/20 text-blue-400",
      admissions_officer: "bg-green-500/20 text-green-400",
      bursar: "bg-yellow-500/20 text-yellow-400",
      teacher: "bg-cyan-500/20 text-cyan-400",
      helpdesk_officer: "bg-orange-500/20 text-orange-400",
    };
    return colors[role] || "bg-gray-500/20 text-gray-400";
  };

  return (
    <AppShell
      eyebrow="User Administration"
      title="Manage users, roles, and permissions"
      description="Control user access, assign roles, manage permissions, and monitor user activities across the system."
    >
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <>
          <div className="mb-6 flex items-center justify-between gap-4">
            <div className="flex gap-2">
              <Button
                variant={activeTab === "users" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("users"); fetchUsers(); }}
              >
                <User className="mr-2 h-4 w-4" />
                Users
              </Button>
              <Button
                variant={activeTab === "permissions" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("permissions"); fetchPermissions(); }}
              >
                <Shield className="mr-2 h-4 w-4" />
                Permissions
              </Button>
              <Button
                variant={activeTab === "roles" ? "primary" : "secondary"}
                onClick={() => { setActiveTab("roles"); fetchRoleMatrix(); }}
              >
                <Key className="mr-2 h-4 w-4" />
                Role Matrix
              </Button>
            </div>
            {activeTab === "users" && (
              <Button onClick={() => setShowCreateUserDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add User
              </Button>
            )}
          </div>

          {activeTab === "users" && (
            <Card className="p-6">
              <SectionTitle 
                title="System Users" 
                description="All users and their current roles" 
              />
              <div className="mt-4 space-y-4">
                {users.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No users found</p>
                ) : (
                  users.map((user) => (
                    <div key={user.id} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex items-center gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#d9a441]/20">
                          <User className="h-5 w-5 text-[#d9a441]" />
                        </div>
                        <div>
                          <p className="font-medium text-white">{user.full_name}</p>
                          <p className="text-sm text-[#9eb1cf]">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className={getRoleColor(user.role)}>
                          {user.role}
                        </Badge>
                        <Badge className={user.status === 'active' ? "border-green-500/30 text-green-500" : "border-red-500/30 text-red-500"}>
                          {user.status}
                        </Badge>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                            Edit
                          </Button>
                          <Button size="sm" variant="outline" className="border-red-500/30 text-red-500 hover:bg-red-500/10">
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "permissions" && (
            <Card className="p-6">
              <SectionTitle 
                title="Permission Management" 
                description="Grant and revoke specific permissions to users" 
              />
              <div className="mt-4 space-y-4">
                {permissions.length === 0 ? (
                  <p className="text-center text-[#9eb1cf]">No permissions data available</p>
                ) : (
                  permissions.map((perm) => (
                    <div key={perm.id} className="flex items-start justify-between rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <p className="font-medium text-white">{perm.user_name}</p>
                          <Badge className="border-white/20 text-white">
                            {perm.email}
                          </Badge>
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {perm.permissions?.map((permission: string) => (
                            <Badge key={permission} className="bg-green-500/20 text-green-400">
                              {permission}
                            </Badge>
                          )) || <span className="text-sm text-[#9eb1cf]">No custom permissions</span>}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => perm.user_id && handleGrantPermission(perm.user_id, "custom_permission")}
                          variant="outline"
                          className="border-green-500/30 text-green-500 hover:bg-green-500/10"
                        >
                          Grant
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => perm.user_id && handleRevokePermission(perm.user_id, "custom_permission")}
                          variant="outline"
                          className="border-red-500/30 text-red-500 hover:bg-red-500/10"
                        >
                          Revoke
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          )}

          {activeTab === "roles" && (
            <Card className="p-6">
              <SectionTitle 
                title="Role Permission Matrix" 
                description="Overview of permissions assigned to each role" 
              />
              <div className="mt-4 overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="px-4 py-2 text-left text-sm font-medium text-[#9eb1cf]">Role</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-[#9eb1cf]">Permissions</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-[#9eb1cf]">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {roleMatrix?.roles?.map((role) => (
                      <tr key={role.name} className="border-b border-white/10">
                        <td className="px-4 py-3">
                          <Badge className={getRoleColor(role.name)}>
                            {role.name}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1">
                            {role.permissions?.slice(0, 3).map((perm: string) => (
                              <Badge key={perm} className="border-white/20 text-white text-xs">
                                {perm}
                              </Badge>
                            ))}
                            {role.permissions?.length > 3 && (
                              <Badge className="border-white/20 text-white text-xs">
                                +{role.permissions.length - 3} more
                              </Badge>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Button size="sm" variant="outline" className="border-[#d9a441]/30 text-[#d9a441] hover:bg-[#d9a441]/10">
                            Edit
                          </Button>
                        </td>
                      </tr>
                    )) || <tr><td colSpan={3} className="px-4 py-3 text-center text-[#9eb1cf]">No role matrix data available</td></tr>}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}
    </AppShell>
  );
}
