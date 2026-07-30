from pathlib import Path
import re

path = Path("tests/test_api.py")
text = path.read_text()

helper = """client = TestClient(app)\n\n\ndef get_auth_headers() -> dict[str, str]:\n    login_response = client.post(\n        \"/api/v1/auth/login\",\n        json={\"email\": \"admin@greenfieldcollege.ng\", \"password\": \"password123\"},\n    )\n    assert login_response.status_code == 200\n    token = login_response.json()[\"access_token\"]\n    return {\"Authorization\": f\"Bearer {token}\"}\n\n\ndef test_health_endpoint() -> None:\n"""
text = text.replace("client = TestClient(app)\n\n", helper)

patterns = [
    (r"(client\.post\(\n\s+\"/api/v1/leads\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.patch\(\n\s+\"/api/v1/leads/LD-104\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.post\(\n\s+\"/api/v1/invoices\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.post\(\n\s+\"/api/v1/payments\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.post\(\n\s+\"/api/v1/messages/broadcast\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.post\(\n\s+\"/api/v1/tickets\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
    (r"(client\.patch\(\n\s+\"/api/v1/tickets/TK-310\",\n\s+json=\{[^}]+\},\n\s*\))(\n)", r"\1,\n        headers=get_auth_headers()\2"),
]

for pat, repl in patterns:
    text, n = re.subn(pat, repl, text, flags=re.MULTILINE)
    if n == 0:
        raise RuntimeError(f"pattern not found: {pat}")

text = re.sub(r"(response = client\.get\(\"/api/v1/reports/admissions\"\))(\n)", r"\1, headers=get_auth_headers()\2", text)
path.write_text(text)
print("updated tests/test_api.py")
