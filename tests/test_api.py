from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_auth_headers() -> dict[str, str]:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_endpoint() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["role"] == "school_admin"


def test_dashboard_summary_endpoint() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["schoolName"] == "Greenfield College, Abuja"
    assert len(payload["kpis"]) == 4


def test_finance_endpoint() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/finance/overview", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["collectionRate"] == "79%"
    assert len(payload["debtors"]) == 3


def test_parents_endpoint_requires_auth() -> None:
    response = client.get("/api/v1/parents")

    assert response.status_code == 401


def test_parents_endpoint_with_auth() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/parents", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["parents"], list)
    assert payload["parents"][0]["name"] == "Mrs. Adeyemi"


def test_refresh_endpoint() -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@greenfieldcollege.ng", "password": "password123"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["token_type"] == "bearer"


def test_create_lead_endpoint() -> None:
    response = client.post(
        "/api/v1/leads",
        json={
            "firstName": "Test",
            "lastName": "Lead",
            "source": "manual",
            "stage": "New Leads",
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["childName"] == "Test Lead"


def test_update_lead_endpoint() -> None:
    response = client.patch(
        "/api/v1/leads/LD-104",
        json={"stage": "Tour Scheduled", "followUpAt": "2026-08-01T10:00:00Z"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["stage"] == "Tour Scheduled"


def test_create_invoice_endpoint() -> None:
    response = client.post(
        "/api/v1/invoices",
        json={
            "studentId": "ST-2034",
            "term": "2026 Third Term",
            "amountDue": 620000,
            "dueDate": "2026-08-01",
            "lineItems": [{"code": "FEE-TU", "description": "Tuition", "amount": 620000}],
        },
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "INV-9999"


def test_record_payment_endpoint() -> None:
    response = client.post(
        "/api/v1/payments",
        json={"invoiceId": "INV-9999", "amount": 620000, "method": "cash", "paidAt": "2026-07-30T10:00:00Z"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["invoiceId"] == "INV-9999"


def test_broadcast_message_endpoint() -> None:
    response = client.post(
        "/api/v1/messages/broadcast",
        json={"audience": "all", "channel": "email", "templateId": "MT-001"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_create_ticket_endpoint() -> None:
    response = client.post(
        "/api/v1/tickets",
        json={"subject": "Sample issue", "priority": "Medium"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "TK-399"


def test_update_ticket_endpoint() -> None:
    response = client.patch(
        "/api/v1/tickets/TK-310",
        json={"status": "in_progress"},
        headers=get_auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_report_detail_endpoint() -> None:
    response = client.get("/api/v1/reports/admissions", headers=get_auth_headers())
    assert response.status_code == 200
    payload = response.json()
    assert payload["reportName"] == "admissions"


def test_forgot_password_endpoint() -> None:
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "admin@greenfieldcollege.ng"},
    )

    assert response.status_code == 200
    assert "reset link" in response.json()["message"].lower()


def test_reset_password_endpoint() -> None:
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "demo-token", "newPassword": "newpassword123"},
    )

    assert response.status_code == 200
    assert "successfully updated" in response.json()["message"].lower()
