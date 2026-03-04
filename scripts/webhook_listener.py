#!/usr/bin/env python3
"""
GitHub Webhook Listener — Narco995/Vm
Listens for GitHub push events and auto-deploys instantly.
Run: python3 scripts/webhook_listener.py
"""
import asyncio
import hashlib
import hmac
import json
import logging
import os
import subprocess
from aiohttp import web

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
DEPLOY_SCRIPT = os.path.join(os.path.dirname(__file__), "../deploy/deploy.sh")
PORT = int(os.getenv("WEBHOOK_PORT", 9001))
ALLOWED_BRANCH = os.getenv("DEPLOY_BRANCH", "main")


def verify_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret set
    mac = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256)
    expected = f"sha256={mac.hexdigest()}"
    return hmac.compare_digest(expected, signature)


async def handle_webhook(request: web.Request) -> web.Response:
    # Verify GitHub signature
    sig = request.headers.get("X-Hub-Signature-256", "")
    body = await request.read()

    if WEBHOOK_SECRET and not verify_signature(body, sig):
        log.warning("Invalid webhook signature!")
        return web.Response(status=401, text="Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")

    if event == "ping":
        log.info("GitHub ping received ✓")
        return web.json_response({"status": "pong"})

    if event != "push":
        return web.json_response({"status": "ignored", "event": event})

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    branch = payload.get("ref", "").replace("refs/heads/", "")
    pusher = payload.get("pusher", {}).get("name", "unknown")
    commit = payload.get("head_commit", {}).get("message", "")[:60]

    log.info(f"Push event: branch={branch} pusher={pusher} commit='{commit}'")

    if branch != ALLOWED_BRANCH:
        log.info(f"Skipping branch: {branch}")
        return web.json_response({"status": "skipped", "branch": branch})

    # Trigger deploy in background
    log.info(f"🚀 Triggering deploy for branch: {branch}")
    asyncio.create_task(run_deploy(branch, pusher, commit))

    return web.json_response({
        "status": "deploying",
        "branch": branch,
        "commit": commit,
        "pusher": pusher
    })


async def run_deploy(branch: str, pusher: str, commit: str):
    log.info(f"Running deploy script for {branch}...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", DEPLOY_SCRIPT, branch,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(DEPLOY_SCRIPT)
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=300)
        output = stdout.decode() if stdout else ""

        if proc.returncode == 0:
            log.info(f"✅ Deploy successful! Branch={branch} by {pusher}")
            log.info(f"Output:\n{output[-1000:]}")
        else:
            log.error(f"❌ Deploy failed! Return code: {proc.returncode}")
            log.error(f"Output:\n{output[-2000:]}")
    except asyncio.TimeoutError:
        log.error("Deploy timed out after 5 minutes!")
    except Exception as e:
        log.error(f"Deploy error: {e}")


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok",
        "service": "vm-webhook-listener",
        "port": PORT,
        "branch": ALLOWED_BRANCH
    })


async def handle_status(request: web.Request) -> web.Response:
    """Show running containers."""
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "../deploy/docker-compose.yml", "ps", "--format", "json"],
            capture_output=True, text=True, cwd=os.path.dirname(__file__), timeout=10
        )
        return web.json_response({"containers": result.stdout, "status": "ok"})
    except Exception as e:
        return web.json_response({"error": str(e)})


def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/status", handle_status)

    print(f"🔗 GitHub Webhook Listener starting on port {PORT}")
    print(f"📌 Add this webhook URL to GitHub:")
    print(f"   http://YOUR-SERVER-IP:{PORT}/webhook")
    print(f"📋 Events to send: Just the push event")
    print(f"🔒 Content type: application/json")
    if WEBHOOK_SECRET:
        print(f"✅ Signature verification: enabled")
    else:
        print(f"⚠️  Set GITHUB_WEBHOOK_SECRET for security")

    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
