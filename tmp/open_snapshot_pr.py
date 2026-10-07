"""Use the existing Git credential in memory; never print or persist it."""
import json
import os
import subprocess

credential = subprocess.run(
    ["git", "credential", "fill"],
    input="protocol=https\nhost=github.com\n\n", text=True,
    capture_output=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
)
fields = dict(line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line)
if credential.returncode or not fields.get("password"):
    raise SystemExit("No GitHub credential available; PR not created.")
env = {**os.environ, "GH_TOKEN": fields["password"]}
gh = "models/tools/gh/bin/gh.exe"
repo = "Silentarcherjr/scayl-sala-de-inteligencia-editorial"
result = subprocess.run([gh, "pr", "list", "--repo", repo, "--head", "worker-b/snapshot",
                         "--base", "main", "--json", "url"], env=env, capture_output=True, text=True)
if result.returncode:
    raise SystemExit("GitHub PR lookup failed; no PR mutation attempted.")
existing = json.loads(result.stdout)
if existing:
    print(existing[0]["url"])
else:
    subprocess.run([gh, "pr", "create", "--repo", repo, "--head", "worker-b/snapshot",
                    "--base", "main", "--draft", "--title",
                    "data: snapshot acquisition and portable manifest (B-01/B-02)",
                    "--body-file", "tmp/snapshot-pr.md"], env=env, check=True)
