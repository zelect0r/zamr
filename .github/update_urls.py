#!/usr/bin/env python3
"""Rewrite MMRL module download URLs to direct upstream release URLs.

mmrl-util's `sync` + `index` re-hosts every module ZIP on this repository's
GitHub Pages (base_url/modules/<id>/<file>.zip). Those ZIPs are never
committed (they are *.zip and several exceed GitHub's 100 MB per-file limit),
so the generated links are broken (404) and modules cannot be installed or
updated.

This script mutates the `zipUrl`/`size` of each module's newest version in
`modules/<id>/update.json` and `json/modules.json`, pointing them at the
canonical upstream release asset. Only version URLs are changed; all other
metadata produced by mmrl-util is left untouched.

Tracks that opt into `options.gitlab.all_versions` are rebuilt from their
GitLab project's release history, so every published build stays installable
instead of only the newest one.

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
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

REPO_URL_RE = re.compile(
    r"(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/.]+)(?:\.git)?"
)
GITLAB_REPO_URL_RE = re.compile(r"https?://gitlab\.com/([^/]+)/([^/?#]+)")
GITLAB_API = "https://gitlab.com/api/v4"
USER_AGENT = "zamr-updater"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, obj):
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def api_get(url: str, token: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
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


def gitlab_repo_pair(url: str):
    m = GITLAB_REPO_URL_RE.match(url or "")
    if not m:
        return None
    repo = m.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]
    return m.group(1), repo


def version_code_from_tag(tag: str):
    """Map a release tag like `v1.0.5` to the module's versionCode (105)."""
    digits = re.findall(r"\d+", tag or "")
    return int("".join(digits)) if digits else 0


def parse_timestamp(value: str):
    if not value:
        return int(time.time())
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return int(time.time())


def head_size(url: str):
    headers = {"User-Agent": USER_AGENT}
    req = Request(url, method="HEAD", headers=headers)
    try:
        with urlopen(req, timeout=60) as resp:
            length = resp.headers.get("Content-Length")
            return int(length) if length else 0
    except (HTTPError, URLError, OSError, ValueError) as exc:
        print(f"  head error for {url}: {exc}")
        return 0


def fetch_gitlab_versions(owner: str, repo: str, module_id: str, variant: str = "default"):
    """Return every installable release of a GitLab project, newest first.

    GitLab hosts the release ZIPs as generic package links, so there is no
    GitHub-style release JSON to patch. We rebuild the full version list from
    the project's releases API instead, which also keeps older releases
    installable from MMRL.
    """
    project = quote(f"{owner}/{repo}", safe="")
    url = f"{GITLAB_API}/projects/{project}/releases?per_page=100"
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    try:
        with urlopen(Request(url, headers=headers), timeout=60) as resp:
            releases = json.load(resp)
    except (HTTPError, URLError, OSError) as exc:
        print(f"  gitlab error for {owner}/{repo}: {exc}")
        return []

    versions = []
    for release in releases:
        tag = release.get("tag_name") or ""
        links = (release.get("assets") or {}).get("links") or []
        assets = [
            {
                "name": link.get("name") or "",
                "url": link.get("url") or "",
                "updated_at": release.get("released_at") or release.get("created_at") or "",
            }
            for link in links
            if link.get("url")
        ]
        asset = pick_asset(module_id, assets, variant=variant)
        if asset is None:
            continue
        versions.append(
            {
                "timestamp": parse_timestamp(asset["updated_at"]),
                "version": tag,
                "versionCode": version_code_from_tag(tag),
                "zipUrl": asset["url"],
                "changelog": "",
                "size": head_size(asset["url"]),
            }
        )

    versions.sort(key=lambda v: (v["versionCode"], v["timestamp"]), reverse=True)
    return versions


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


def pick_asset(module_id: str, assets, hint: str = "", variant: str = "default"):
    """Choose the best release asset for a module, preferring a brand match."""
    zips = [a for a in assets if (a.get("name") or "").lower().endswith(".zip")]
    if module_id.startswith("alwaysstrong"):
        # Releases ship three variants (default, -inject, -nopif) that only
        # differ in the fingerprint engine. Each track publishes exactly one
        # of them so all three are selectable in MMRL.
        if variant == "inject":
            zips = [a for a in zips if "-inject" in a["name"].lower()]
        elif variant == "nopif":
            zips = [a for a in zips if "-nopif" in a["name"].lower()]
        else:
            zips = [
                a
                for a in zips
                if "-inject" not in a["name"].lower() and "-nopif" not in a["name"].lower()
            ]
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
    url = f"https://api.github.com/repos/{gh}/{repo}/releases?per_page=1"
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

        update_file = track_file.parent / "update.json"
        if not update_file.is_file():
            print(f"[{module_id}] no update.json, skipping")
            continue

        # Some upstreams moved off GitHub. For tracks that opt into
        # `options.gitlab.all_versions`, rebuild the complete release history
        # from the GitLab releases API so older builds stay installable.
        options = track.get("options") or {}
        gitlab_options = options.get("gitlab") or {}
        if gitlab_options.get("all_versions"):
            gitlab_pair = gitlab_repo_pair(
                track.get("source") or track.get("homepage") or track.get("update_to") or ""
            )
            if not gitlab_pair:
                print(f"[{module_id}] no GitLab repository configured, skipping")
                continue

            variant = gitlab_options.get("variant", "default")
            versions = fetch_gitlab_versions(*gitlab_pair, module_id, variant)
            if not versions:
                print(f"[{module_id}] no GitLab releases found, leaving as-is")
                continue

            update_json = load_json(update_file)
            # A failed HEAD request yields size 0; keep the size we already
            # published for that release instead of churning the index.
            previous = {
                version.get("version"): version
                for version in (update_json.get("versions") or [])
            }
            for version in versions:
                old = previous.get(version["version"])
                if old and not version["size"]:
                    version["size"] = old.get("size", 0)
                if old and version["zipUrl"] == old.get("zipUrl") and not version["changelog"]:
                    version["changelog"] = old.get("changelog", "")

            latest = versions[0]
            if update_json.get("versions") != versions:
                changed = True
                update_json["versions"] = versions
                update_json["version"] = latest["version"]
                update_json["versionCode"] = latest["versionCode"]
                dump_json(update_file, update_json)
                print(f"[{module_id}] update.json  -> {len(versions)} releases")

            mod = index_modules.get(module_id)
            if mod is not None:
                name = gitlab_options.get("name")
                description = gitlab_options.get("description")
                if (
                    mod.get("versions") != versions
                    or mod.get("version") != latest["version"]
                    or mod.get("versionCode") != latest["versionCode"]
                    or mod.get("size") != latest["size"]
                    or (name is not None and mod.get("name") != name)
                    or (description is not None and mod.get("description") != description)
                ):
                    changed = True
                mod["versions"] = versions
                mod["version"] = latest["version"]
                mod["versionCode"] = latest["versionCode"]
                mod["size"] = latest["size"]
                if name is not None:
                    mod["name"] = name
                if description is not None:
                    mod["description"] = description
                print(f"[{module_id}] modules.json -> {len(versions)} releases")
            continue

        pair = repo_pair(track.get("update_to") or "")
        if not pair:
            print(f"[{module_id}] not a GitHub repo, skipping")
            continue

        owner, repo = pair
        # The previously published ZIP name is a good hint when upstream asset
        # names do not obviously match the module id (e.g. TrickyAddonModule).
        hint = ""
        prev = load_json(update_file)
        prev_versions = prev.get("versions") or []
        if prev_versions:
            prev_url = prev_versions[0].get("zipUrl") or ""
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
