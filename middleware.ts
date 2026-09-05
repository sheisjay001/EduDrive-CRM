import { NextResponse, type NextRequest } from "next/server";

const AUTH_COOKIE = "edudrive_auth";
const ROLE_COOKIE = "edudrive_role";

export const ROLE_HOME_MAP: Record<string, string> = {
  super_admin: "/dashboard/super-admin",
  school_admin: "/dashboard/school-admin",
  admissions_officer: "/dashboard/admissions",
  bursar: "/dashboard/bursar",
  teacher: "/dashboard/teacher",
  helpdesk_officer: "/dashboard/helpdesk",
  parent: "/dashboard/parent",
  student: "/dashboard/student",
};

const PUBLIC_PATHS = new Set([
  "/",
  "/login",
  "/parent-login",
  "/student-login",
  "/signup",
  "/forgot-password",
  "/reset-password",
  "/favicon.ico",
]);

const STAFF_ROLES = [
  "super_admin",
  "school_admin",
  "admissions_officer",
  "bursar",
  "teacher",
  "helpdesk_officer",
];

const PATH_ROLES: Array<{ pattern: RegExp; roles: string[] }> = [
  { pattern: /^\/dashboard\/super-admin(\/|$)/, roles: ["super_admin"] },
  { pattern: /^\/dashboard\/school-admin(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/dashboard\/admissions(\/|$)/, roles: ["super_admin", "school_admin", "admissions_officer"] },
  { pattern: /^\/dashboard\/bursar(\/|$)/, roles: ["super_admin", "school_admin", "bursar"] },
  { pattern: /^\/dashboard\/teacher(\/|$)/, roles: ["super_admin", "school_admin", "teacher"] },
  { pattern: /^\/dashboard\/helpdesk(\/|$)/, roles: ["super_admin", "school_admin", "helpdesk_officer"] },
  { pattern: /^\/dashboard\/parent(\/|$)/, roles: ["parent"] },
  { pattern: /^\/dashboard\/student(\/|$)/, roles: ["student"] },

  { pattern: /^\/admissions(\/|$)/, roles: ["super_admin", "school_admin", "admissions_officer"] },
  { pattern: /^\/families(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/finance(\/|$)/, roles: ["super_admin", "school_admin", "bursar"] },
  { pattern: /^\/messaging(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/staff(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/reports(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/settings(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/analytics(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/activity(\/|$)/, roles: ["super_admin", "school_admin"] },
  { pattern: /^\/frontdesk(\/|$)/, roles: ["super_admin", "school_admin"] },
];

function isPublic(pathname: string): boolean {
  if (PUBLIC_PATHS.has(pathname)) return true;
  if (pathname.startsWith("/_next") || pathname.startsWith("/api")) return true;
  if (/\.(png|jpg|jpeg|svg|css|js|woff|woff2|ttf|ico|webp|gif)$/i.test(pathname)) return true;
  return false;
}

function isPathAllowedForRole(pathname: string, role: string): boolean {
  const entry = PATH_ROLES.find(r => r.pattern.test(pathname));
  if (!entry) {
    return true;
  }
  return entry.roles.includes(role);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublic(pathname)) {
    return NextResponse.next();
  }

  const authCookie = request.cookies.get(AUTH_COOKIE)?.value;
  const roleCookie = request.cookies.get(ROLE_COOKIE)?.value;

  if (!authCookie) {
    const loginPage =
      pathname.startsWith("/dashboard/parent") ? "/parent-login" :
      pathname.startsWith("/dashboard/student") ? "/student-login" :
      "/login";
    const url = request.nextUrl.clone();
    url.pathname = loginPage;
    url.searchParams.set("redirect", pathname);
    return NextResponse.redirect(url);
  }

  const role = roleCookie || "school_admin";

  if (!isPathAllowedForRole(pathname, role)) {
    const home = ROLE_HOME_MAP[role] || "/dashboard";
    const url = request.nextUrl.clone();
    url.pathname = home;
    url.searchParams.delete("redirect");
    return NextResponse.redirect(url);
  }

  if (STAFF_ROLES.includes(role)) {
    if (pathname.startsWith("/dashboard/parent") || pathname.startsWith("/dashboard/student")) {
      const home = ROLE_HOME_MAP[role] || "/dashboard";
      const url = request.nextUrl.clone();
      url.pathname = home;
      return NextResponse.redirect(url);
    }
  }

  if (role === "parent") {
    const staffOnly = ["/admissions/", "/families/", "/staff/"];
    if (staffOnly.some(p => pathname.startsWith(p.replace(/\/$/, "")))) {
      const url = request.nextUrl.clone();
      url.pathname = "/dashboard/parent";
      return NextResponse.redirect(url);
    }
  }

  if (role === "student") {
    const studentForbidden = [
      "/admissions", "/families", "/parents", "/finance", "/staff", "/settings", "/analytics", "/activity", "/frontdesk",
    ];
    if (studentForbidden.some(p => pathname === p || pathname.startsWith(p + "/"))) {
      const url = request.nextUrl.clone();
      url.pathname = "/dashboard/student";
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
