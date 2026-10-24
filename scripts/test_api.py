#!/usr/bin/env python3
"""End-to-end API flow test for AI Chatbot Cloud."""

import json
import sys
import time
import urllib.error
import urllib.request
import uuid

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost"


def req(method: str, path: str, data=None, token: str | None = None, files=None):
    url = f"{BASE}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if files:
        boundary = uuid.uuid4().hex
        body = b""
        for name, filename, content, ctype in files:
            chunk = content.encode("utf-8") if isinstance(content, str) else content
            body += (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f"Content-Type: {ctype}\r\n\r\n"
            ).encode()
            body += chunk + b"\r\n"
        body += f"--{boundary}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
    elif data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
        r = urllib.request.Request(url, data=body, headers=headers, method=method)
    else:
        r = urllib.request.Request(url, headers=headers, method=method)

    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"raw": raw}
        return e.code, detail


def check(name: str, condition: bool, detail="") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print(f"\n=== AI Chatbot API Tests ({BASE}) ===\n")
    passed = 0
    total = 0

    def run(name, cond, detail=""):
        nonlocal passed, total
        total += 1
        if check(name, cond, detail):
            passed += 1

    print("1. Health & connectivity")
    code, body = req("GET", "/health")
    run("Service /health", code == 200)

    code, body = req("GET", "/api/health")
    run("Backend /api/health", code == 200 and body.get("status") == "healthy")

    code, _ = req("GET", "/api/auth/me")
    run("API auth guard (401)", code == 401)

    print("\n2. Authentication")
    email = f"test_{int(time.time())}@example.com"
    password = "testpass123"

    code, body = req(
        "POST",
        "/api/auth/register",
        {"email": email, "password": password, "full_name": "Test User"},
    )
    run("Register", code == 201, str(body))

    code, body = req("POST", "/api/auth/login", {"email": email, "password": password})
    token = body.get("access_token")
    refresh = body.get("refresh_token")
    run("Login", code == 200 and bool(token))

    code, body = req("GET", "/api/auth/me", token=token)
    run("Get profile", code == 200 and body.get("email") == email)

    code, body = req("POST", "/api/auth/refresh", {"refresh_token": refresh})
    if code == 200:
        token = body.get("access_token", token)
    run("Refresh token", code == 200)

    print("\n3. Documents")
    test_txt = (
        "AI Chatbot Cloud is an embedding-based RAG system. "
        "It uses Sentence Transformers and ChromaDB for document retrieval. "
        "Users can upload PDF and TXT files to build a personal knowledge base."
    )
    code, body = req(
        "POST",
        "/api/documents/upload",
        token=token,
        files=[("file", "test-knowledge.txt", test_txt, "text/plain")],
    )
    doc_id = body.get("id")
    run("Upload TXT", code == 201 and body.get("status") == "ready", str(body))

    code, body = req("GET", "/api/documents", token=token)
    run("List documents", code == 200 and len(body) >= 1)

    print("\n4. Chat / RAG")
    code, body = req("POST", "/api/chat/conversations", {"title": "Test Chat"}, token=token)
    conv_id = body.get("id")
    run("Create conversation", code == 201 and bool(conv_id))

    code, body = req(
        "POST",
        f"/api/chat/conversations/{conv_id}/messages",
        {"message": "What is AI Chatbot Cloud and what technologies does it use?"},
        token=token,
    )
    answer = body.get("message", {}).get("content", "")
    sources = body.get("sources", [])
    run(
        "Send message (RAG)",
        code == 200 and len(answer) > 0,
        f"len={len(answer)}, sources={len(sources)}",
    )

    code, body = req("GET", f"/api/chat/conversations/{conv_id}/messages", token=token)
    run("Message history", code == 200 and len(body) >= 2)

    code, body = req("GET", "/api/chat/conversations", token=token)
    run("List conversations", code == 200 and len(body) >= 1)

    print("\n5. Monitoring")
    code, body = req("GET", "/api/monitoring/stats", token=token)
    run("Stats", code == 200 and "users" in body, str(body.get("services")))

    print("\n6. Cleanup")
    if doc_id:
        code, _ = req("DELETE", f"/api/documents/{doc_id}", token=token)
        run("Delete document", code == 204)
    if conv_id:
        code, _ = req("DELETE", f"/api/chat/conversations/{conv_id}", token=token)
        run("Delete conversation", code == 204)

    print(f"\n=== Results: {passed}/{total} passed ===\n")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
