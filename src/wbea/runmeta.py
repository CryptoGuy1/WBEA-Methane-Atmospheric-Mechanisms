import json, subprocess, datetime, platform, hashlib
from .config import ROOT, CFG

def _git(*a):
    try: return subprocess.check_output(["git", *a], cwd=ROOT, text=True).strip()
    except Exception: return None

# git state captured when the experiment script imports this module, i.e. BEFORE it writes outputs
_START = dict(commit=_git("rev-parse", "HEAD"), dirty=bool(_git("status", "--porcelain")))

def write(exp_dir, extra=None):
    meta = dict(run_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                git_commit_at_run=_START["commit"], git_dirty_at_start=_START["dirty"],
                python=platform.python_version(), seed=CFG["project"]["seed"],
                requirements_sha256=hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest(),
                config_sha256=hashlib.sha256((ROOT / "config" / "project.toml").read_bytes()).hexdigest(),
                dev_panel_manifest_sha256=hashlib.sha256((ROOT / "manifests" / "dev_panel_SHA256SUMS.txt").read_bytes()).hexdigest())
    meta.update(extra or {})
    (exp_dir / "run_metadata.json").write_text(json.dumps(meta, indent=1))
    return meta
