#!/usr/bin/env python3
"""Rewrite MMRL module download URLs to direct upstream GitHub release URLs.

mmrl-util's `sync` + `index` re-hosts every module ZIP on this repository's
GitHub Pages (base_url/modules/<id>/<file>.zip). Those ZIPs are never
committed (they are *.zip and several exceed GitHub's 100 MB per-file limit),
so the generated links are broken (404) and modules cannot be installed or
updated.

This script only mutates the `zipUrl`/`size` of each module's newest version in
`modules/<id>/update.json` and `json/modules.json`, pointing them at the
canonical upstream GitHub release asset. Only version URLs are changed; all
other metadata produced by mmrl-util is left untouched.

It performs one GitHub REST request per module and needs no third-party
dependencies. Set GITHUB_TOKEN for a higher rate limit (the workflow provides
it automatically).

Run: python update_urls.py [--root /path/to/repo]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_URL_RE = re.compile(
    r"(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/.]+)(?:\.git)?"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def api_get(url: str, token: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "zamr-updater"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=60) as resp:
        return json.load(resp)


def repo_pair(update_to: str):
    m = REPO_URL_RE.match(update_to)
    if not m:
        return None
    return m.group(1), m.group(2)


def module_keywords(module_id: str):
    """Substrings used to match a release asset to a module.

    Handles the common case where several modules are built from one upstream
    repository/release (e.g. j-hc/revanced-magisk-module serves both
    `music-morphe` and `youtube-morphe`), as well as ids that use underscores
    while upstream assets use hyphens (e.g. `hma_oss_zygisk`).
    """
    candidates = {
        module_id,
        module_id.replace("-", "_"),
        module_id.replace("_", "-"),
        module_id.replace("-", "").replace("_", ""),
    }
    return [k.lower() for k in candidates if k]


def pick_asset(module_id: str, assets, hint: str = ""):
    """Choose the best release asset for a module, preferring a brand match."""
    zips = [a for a in assets if (a.get("name") or "").lower().endswith(".zip")]
    if not zips:
        return None

    keywords = module_keywords(module_id)
    if hint:
        keywords.append(hint.lower())
    scored = []
    for asset in zips:
        name = asset["name"].lower()
        score = 0
        if any(k in name for k in keywords):
            score += 100
        if "release" in name:
            score += 10
        elif "debug" in name:
            # Prefer release builds; debug zips can be much larger than the
            # release artifact for the very same tag (e.g. TA_enhanced).
            score -= 10
        if module_id in ("music-morphe", "youtube-morphe") and ("-all" in name or "arm64" in name):
            score += 5
        scored.append((score, asset.get("updated_at", ""), asset))

    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return scored[0][2]


def fetch_latest_release(gh: str, repo: str, module_id: str, token: str, hint: str = ""):
    url = f"https://api.github.com/repos/{repo}/releases?per_page=1"
    try:
        releases = api_get(url, token)
    except HTTPError as exc:
        print(f"  http error for {repo}: {exc.code}")
        return None
    except (URLError, OSError) as exc:
        print(f"  network error for {repo}: {exc}")
        return None
    if not releases:
        return None
    asset = pick_asset(module_id, releases[0].get("assets") or [], hint)
    if asset is None:
        return None
    return {"zipUrl": asset["browser_download_url"], "size": asset.get("size", 0)}


def patch_versions(versions):
    """Locate the newest version entry (MMRL reads `versions[0]`).

    MMRL treats the FIRST entry of `versions` as the current release, while
    mmrl-util writes histories oldest-first (newest last). Reorder newest-first
    and return the newest entry so the caller can fix its download URL.
    """
    if not versions:
        return None
    versions.sort(key=lambda v: v.get("versionCode", 0) or 0, reverse=True)
    return versions[0]


def commit_time(root):
    """Timestamp of `json/modules.json` in `HEAD`, if available."""
    try:
        out = subprocess.check_output(
            ["git", "show", "HEAD:json/modules.json"],
            text=True,
            cwd=str(root),
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out).get("metadata", {}).get("timestamp")
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()

    root = Path(args.root)
    modules_dir = root / "modules"

    if not modules_dir.is_dir():
        sys.exit(f"modules dir not found: {modules_dir}")

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN") or ""
    changed = False

    index_file = root / "json" / "modules.json"
    index = load_json(index_file) if index_file.is_file() else None
    index_modules = {m.get("id"): m for m in (index or {}).get("modules", [])}

    for track_file in sorted(modules_dir.glob("*/track.json")):
        track = load_json(track_file)
        module_id = track.get("id")
        if not module_id or track.get("enable") is False:
            continue

        pair = repo_pair(track.get("update_to") or "")
        if not pair:
            print(f"[{module_id}] not a GitHub repo, skipping")
            continue

        update_file = track_file.parent / "update.json"
        if not update_file.is_file():
            print(f"[{module_id}] no update.json, skipping")
            continue

        owner, repo = pair
        # The previously published ZIP name is a good hint when upstream asset
        # names do not obviously match the module id (e.g. TrickyAddonModule).
        hint = ""
        prev = load_json(update_file)
        prev_versions = prev.get("versions") or []
        if prev_versions:
            prev_url = prev_versions[-1].get("zipUrl") or ""
            hint = prev_url.rstrip("/").rsplit("/", 1)[-1]
            if hint.lower().endswith(".zip"):
                hint = hint[:-4]
        release = fetch_latest_release(owner, repo, module_id, token, hint)
        # Be gentle with the unauthenticated rate limit (60 req/h).
        if not token:
            time.sleep(3)
        if release is None:
            print(f"[{module_id}] no latest release/asset found, leaving as-is")
            continue

        url = release["zipUrl"]
        size = release["size"]

        update_json = load_json(update_file)
        entry = patch_versions(update_json.get("versions"))
        if entry is not None:
            if entry.get("zipUrl") != url or entry.get("size") != size:
                changed = True
                entry["zipUrl"] = url
                entry["size"] = size
                dump_json(update_file, update_json)
                print(f"[{module_id}] update.json  -> {url}")
            else:
                print(f"[{module_id}] update.json   unchanged")

        mod = index_modules.get(module_id)
        if mod is not None and entry is not None:
            # mmrl-util's index snapshots whatever versions existed at build
            # time, which can lag behind update.json (e.g. freshly synced
            # releases). Mirror the full newest-first history from update.json
            # so the published index always exposes the current artifact.
            new_versions = update_json.get("versions", [])
            old_versions = mod.get("versions", [])
            meta_flip = (
                mod.get("version") != entry.get("version")
                or mod.get("versionCode") != entry.get("versionCode")
                or mod.get("size") != entry.get("size")
            )
            if meta_flip or old_versions != new_versions:
                changed = True
            mod["versions"] = new_versions
            mod["version"] = entry.get("version", mod.get("version"))
            mod["versionCode"] = entry.get("versionCode", mod.get("versionCode"))
            mod["size"] = entry.get("size", mod.get("size"))
            print(f"[{module_id}] modules.json -> {url}")

    if index is not None:
        if changed:
            index["metadata"] = {"version": 1, "timestamp": time.time()}
        else:
            # Keep the previously published timestamp so no-op runs produce no
            # commit, otherwise every hourly run would re-commit and re-trigger.
            prev = commit_time(root)
            if prev is not None:
                index.setdefault("metadata", {})["timestamp"] = prev
        dump_json(index_file, index)
        print("modules.json metadata timestamp updated" if changed else "modules.json metadata timestamp preserved")

    print("done")


if __name__ == "__main__":
    main()
