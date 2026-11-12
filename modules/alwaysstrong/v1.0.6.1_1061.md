# AlwaysStrong changelog

## v1.0.6.1

**New**
- **Status notification (opt-in, Advanced > Automatic, default off).** When on, AlwaysStrong posts one notification with the current integrity level (STRONG / DEVICE / BASIC / CHANGE KEY) after each hourly check and on every Action. It updates the same notification in place instead of stacking new ones, and only re-posts when the level actually changes, so it never spams. Posting it from the shell user keeps it visible on every root manager.

**Fixes**
- **Install no longer fails on some KernelSU-Next setups.** On a device whose root manager could not create its temp dir (the install log shows "/dev/tmp: No such file or directory"), busybox "mkdir -p" aborted on the root path and the install died with "extract failed". Module subdirectories are now created without that pitfall, and the optional helper binaries (aswatcher, asfetch) warn instead of aborting when they cannot be extracted, so the attestation core still installs.
- **"Block ROM spoof" now also stops Infinity-X's Play Store spoof.** On ProjectInfinity-X's Android 16 scheme, the Play Store kept being spoofed after a reboot because the ROM's real master switch (spoof_pif_enabled) was never turned off. It is now set correctly, verified against the ROM source.

## v1.0.6

**New**
- **Patched TEESimulator-RS keystore (v6.1.0-313).** The bundled attestation engine now carries the open community fixes for Android 17 / KeyMint v5 that upstream has not released yet: A17 Canary injection, correct osVersion / attestVersion / keymasterVersion, a per-instance VINTF scan, an RSA block-mode fix, a cached-response purge so a key survives an app "clear data", and Xiaomi / Redmi / Poco secure-boot alias normalization. Source and the exact PRs are credited under Upstream.
- **"Spoof security patch" is back as an opt-in (Advanced, default off).** When on, it rewrites the system patch date (Settings / getprop) to the attested value for the rare key-attestation checker that compares the two. Off, the default, keeps your device's real patch date, so custom-ROM users no longer see it frozen. Play Integrity is unaffected either way (it reads the patch through the fingerprint hook and the TEE attestation).

**Fixes**
- **The monthly security patch reaches every device again.** The fingerprint fetch pulled only from `raw.githubusercontent.com`, which is throttled or blocked on some carriers; with no Pixel 6 fallback on the flashstation API, the hourly refresh there failed silently and the phone stayed frozen on an older month's patch. Both the automatic refresh and the beta picker now fall back to a jsDelivr CDN mirror of the same repo, so a blocked GitHub host no longer strands a device on a stale patch.
- **A picked or imported fingerprint takes effect right away.** The Play Integrity recycle reaches Google's DroidGuard sandbox through `am kill` (which `killall` cannot signal), so a new fingerprint or keybox applies without force-closing Play Store by hand.
- **The WebUI tells the truth while applying.** Selecting a fingerprint shows a real "Applying → Applied" (and surfaces the actual error on failure) instead of flashing straight to "Applied" before anything landed.
- **The beta picker accepts an already-complete Canary fingerprint** instead of reporting "engine rejected the fingerprint".
- **Better ROM-spoof blocking for custom ROMs.** "Block ROM spoof" now also neutralizes ProjectInfinity-X on its newer schemes (the Android 16 / 17 Settings.Secure keys, not just the older PixelProps / pihooks props); every change is backed up and restored on uninstall.
- **LineageOS Updater works again.** "Hide ROM identity" no longer clears the `ro.lineage.*` build props the Updater reads, so OTA checks keep working; only the cosmetic ROM markers are hidden.

**Changed**
- **Faster fingerprint apply.** The STRONG spoof flags are enforced in a single native pass (`asfetch enforce-spoof`) rather than a `sed` + `grep` spawned per prop file, and the four settings writes are batched into one. Every step falls back to the pure-shell path on any device without a native prebuilt, so behaviour is identical everywhere.
- **Detector apps are targeted automatically.** Known integrity-detector apps (Duck Detector and others) are added to the target list in generate mode by default, like the Play stack.
- **The beta fingerprint picker no longer labels a print "STRONG".** Reaching STRONG depends on the device (only models that launched on Android 12 or earlier can), not on the fingerprint alone, so the badge was misleading.

**Upstream**
- Keystore: [TEESimulator-RS](https://github.com/Enginex0/TEESimulator-RS) v6.0.1-307 plus open PRs [#68](https://github.com/Enginex0/TEESimulator-RS/pull/68) and [#73](https://github.com/Enginex0/TEESimulator-RS/pull/73) (Android 17 / KeyMint v5), [#63](https://github.com/Enginex0/TEESimulator-RS/pull/63) (RSA block mode), [#77](https://github.com/Enginex0/TEESimulator-RS/pull/77) (cached-response purge) and [#47](https://github.com/Enginex0/TEESimulator-RS/pull/47) (Xiaomi secure-boot aliases). GPL-3.0 open source, thanks to its author and the PR contributors.
- PlayIntegrityFork v19.

**Builds**
- Three release zips: `AlwaysStrong-<ver>.zip` (default / Fork), `-inject.zip`, `-nopif.zip` (Lite), all on the patched TEESimulator-RS.
- Want a different keystore? The TrickyStoreOSS (`-TSOSS`) and TEESimulator-by-JingMatrix (`-TEESIM`) engines stay nightly-only, never in a release: grab a build from the [download table in docs/ADVANCED.md](https://gitlab.com/Evokerr/AlwaysStrong/-/blob/main/docs/ADVANCED.md#optional-keystore-engines--tsoss--teesim) or build with `./build.sh --engine trickystoreoss` / `--engine teesim`.

## v1.0.5

**New**
- **New WebUI design.** The whole panel is redrawn, with an Advanced tab, a theme picker (System / Light / Dark) and a native file picker that sorts, filters to `.xml` and remembers the last folder.
- **Beta fingerprint picker.** Advanced lists Google's current Pixel beta/canary fingerprints; the ones that still pass STRONG (the Pixel 6 series) are badged and sorted to the top.
- **Import your own fingerprint.** Drop a `pif.json` / `pif.prop` to use it as the active fingerprint; the WebUI shows its device name with a button to revert to automatic.
- **"Get security patch" button.** Fills the System / Vendor / Boot patch fields from the active fingerprint's own date.
- **Widevine L1 restore (opt-in).** Advanced action to restore Widevine L1 on Qualcomm devices that lost it.
- **DenyList hides root from the Play stack (Magisk).** The Google Play processes are added to the DenyList at boot so a hider scrubs the module's mounts out of them (entries only, Enforce is never touched).
- **15 languages, fully translated.** Every screen is covered in all 15 languages, not just English and Turkish.

**Changed**
- **The attested security patch follows the fingerprint.** It is written verbatim to system / vendor / boot instead of the current month, with per-partition manual overrides.
- **Automatic and manual fingerprint are mutually exclusive.** Turning Fingerprint on drops a picked or imported one; picking or importing one turns it off.
- **Faster Action on a manual tap.** The cosmetic pauses between steps are trimmed; the bounded network work is unchanged.
- **One config directory.** Every setting lives in one `key=value` file under `alwaysstrong/`, written out in full on install, boot and reset; old marker files are imported and cleared.
- **Faster WebUI.** The first screen loads in one root call and paints its last state instantly, and old WebViews / odd DPIs render correctly (plain `rgba`, font boosting off, long labels wrap).

**Fixes**
- **TEESimulator reaches STRONG on an unlocked bootloader.** The adapter writes the `overrides.json` root of trust (Verified + locked, non-zero boot key, resolved VBMeta digest) on every config push.
- **The panel no longer freezes on a setting change.** Picking or importing a fingerprint, flipping a spoof flag or the patch toggle now runs its work in the background; the control updates at once.
- **An imported or beta fingerprint is the one attested.** The patch sync and Action read the engine's active fingerprint before the stale auto-fetch copy, and importing clears the old copy.
- **Action fetches a STRONG-capable fingerprint.** It pulls a Pixel 6-series Canary fingerprint (the identities that still hold STRONG) instead of the newest Pixel; fallbacks are Pixel 6a / 6.
- **Custom target apps survive a reboot.** The builder now reads the WebUI-added packages list, so a hand-added app sticks.
- **Stable vbmeta digest.** `ro.boot.vbmeta.digest` is resolved deterministically instead of ever falling back to a random value.
- **A shorter check interval takes effect at once.** Writing the interval tells the refresh loop to drop its current wait and restart.
- **Target list taps register.** A tap only has to stay within 12 px; the long-press (per-app keybox / mode) is unaffected, and no Copy / Share bar opens over the dialog.
- **Status indicator comes back at once.** Turning it on fetches and stamps the status right away instead of waiting for the next hourly run.
- **Reset to defaults.** One button puts every WebUI setting back to fresh-install state and re-runs Action, keeping your keybox.
- **Action works on newer Magisk Alpha.** It re-executes under the manager's busybox, so the ash-only line no longer kills it under `mksh`, and the Action rows line up again.
- **Honest keybox status.** Action asks the mirror every tap instead of trusting any keybox-looking file.
- **TEESimulator (JingMatrix) reloads on a keybox / target change** instead of waiting for the first hourly tick. Collect logs is richer and every probe is time-bounded so the button cannot hang.

**Upstream**
- PlayIntegrityFork CI #623 (post-v18, Canary-print fixes), PlayIntegrityFix inject-s v4.9 (from v4.7). TEESimulator-RS kept at v6.0.1-307 per the Telegram poll.

**Builds**
- Three release zips: `AlwaysStrong-<ver>.zip` (default / Fork), `-inject.zip`, `-nopif.zip` (Lite). The TrickyStoreOSS and TEESimulator (JingMatrix) engines stay nightly-only, see `docs/ADVANCED.md`.

## v1.0.4

**New**
- **Lite build** (`-nopif`): hardware attestation + auto keybox, no bundled fingerprint spoof — for setups where the bundled PlayIntegrityFork conflicts with Google Play Services. Drives your own PlayIntegrityFork / Fix if you have one.
- **WebUI Advanced tab**: import your own fingerprint (`pif.json` / `pif.prop`), toggle any spoof flag by name, add custom target packages, select all / unselect unnecessary.
- **Zero-touch first boot**: the first boot after install runs the Action by itself, so a fresh install lands `STRONG` without opening the module.
- Upstream releases now auto-publish (PlayIntegrityFork / PlayIntegrityFix / TEESimulator-RS bumps become a release on their own).

**Fixes**
- **Action no longer gets stuck on a black screen.** Every network step is bounded and falls back to the next downloader; limits are progress-based, so slow networks are never cut off. The native fetcher prefers IPv4 and retries over the other address family when a connection stalls.
- Custom ROMs: ROM version no longer shows "unknown", the LineageOS fast-charging toggle is back, and the security patch follows OTAs again (the aggressive hides are opt-in in the Advanced tab).
- Uninstalling a Lite build no longer removes your own PlayIntegrityFork / Fix.
- The system security-patch date follows the attested patch again (as in v1.0.3), so attestation checkers no longer report "OS patch differs". It never moves the date backwards, and a new **Advanced → Spoof security patch** toggle turns it off.

**Upstream**
- PlayIntegrityFork v18, TEESimulator-RS v6.0.1-307.

**Builds**
- Releases ship three zips: `AlwaysStrong-<ver>.zip` (default), `-inject.zip`, `-nopif.zip` (Lite). The TrickyStoreOSS / TEESimulator (JingMatrix) engines are nightly-only — see `docs/ADVANCED.md`.

## v1.0.3

- Added a second build, `-inject`, running on PlayIntegrityFix inject-s. A lot of you asked for it. Try it if the default doesn't reach STRONG on your device.
- Per-app keybox: assign a different keybox to specific apps from the WebUI, instead of one keybox for everything. Import your own keybox files, pick which app gets which, and the rest keep using the default — handy when one app needs a separate key.
- Collect logs button in the WebUI (also `sh action.sh logs`) that saves a diagnostic report to `/sdcard` for issue reports.
- Updated TEESimulator-RS to v6.0.1-307.
- Bug fixes.

## v1.0.2

New keybox mirror, a far more reliable fetcher, a custom-keybox file picker in the WebUI, strong-integrity fixes, and a faster, steadier Action.

**Strong integrity**
- **The fingerprint reaches PlayIntegrityFork.** PIF's zygisk reads `custom.pif.prop` from the module dir; every fetch path — native, autopif4, and the shipped fallback — now runs `migrate.sh` to produce that file and enforces the STRONG spoof settings (`spoofProvider=0`, `spoofVendingFinger=1`), so STRONG holds with a valid keybox (3 green).
- **Strong survives the hourly refresh.** The hourly fingerprint refresh regenerated `custom.pif.prop` but skipped re-applying the STRONG spoof settings, so ~1 h after boot the fingerprint silently reverted to a weak config (`spoofProvider=1`, `spoofVendingFinger=0`) and STRONG dropped even though the WebUI still showed 3 green. The native fetch now enforces the STRONG settings itself, and the hourly loop re-enforces them, so every refresh stays strong.
- **Faster fingerprint.** The fast native crawl (~10s) is primary; autopif4 — whose crawl stalls up to ~1 min on some devices — is the fallback.

**ROM spoof**
- The disable list now matches PlayIntegrityFork's current engines (adds `persist.sys.pp.*`, plus AOSPA / PixelOS / Afterlife detection). Uninstalling AlwaysStrong now restores the ROM's own spoof engines — the persist props it set are cleared on uninstall (only if still unchanged), so removing the module frees PixelProps / pihooks / entryhooks again.

**Keybox & status**
- Moved to the new mirror: keybox from `http://evoker.qzz.io/key`, status from `/status`.
- The WebUI status now shows which keybox is in use (e.g. `evokerrkey27`) alongside the health.

**Custom keybox (WebUI)**
- New "Custom keybox" toggle — use your own keybox instead of the auto one.
- Built-in file manager to pick a keybox from storage: breadcrumb path, folder navigation, file size + date, and sort (name / newest / oldest).
- While custom keybox is on, the module stops auto-fetching (Action shows "custom keybox — skip fetch").

**Fingerprint**
- The fingerprint is now fetched by a native crawl of the same Google servers PlayIntegrityFork uses — fast and reliable on devices where autopif4's busybox-wget crawl used to hang. autopif4 is kept as a bounded fallback, and shipped static fingerprints guarantee one always lands.
- The Action never shows a bare "offline": a failed primary is shown once as "trying with fallback", and it drops through quickly (bounded timeouts).

**Fetcher (asfetch)**
- Rewritten to connect IPv4-first — fixes "keybox missing" and stuck downloads on networks that advertise IPv6 in DNS but have no working IPv6 route.
- Handles http + https, redirects, chunked responses, and custom request headers.
- Every download (keybox, status, fingerprint crawl, WebUI) falls back across asfetch → busybox wget → curl → wget, so it works on every device.

**Misc**
- Removed the "recheck in ~1 min" line from the Action output.

## v1.0.1

Hotfix, same upstream as v1.0.0.

- Added a native fetcher (Rust/rustls) so the keybox downloads on every device — busybox's TLS was stalling on the mirror.
- Action button no longer hangs, and it stops force-enabling Magisk's Enforce DenyList.
- Smaller banner / lighter zip.

## v1.0.0

Initial release.

- Bundles TEESimulator-RS v6.0.1-282 (Rust TEE simulator, hardware attestation injection)
- Bundles PlayIntegrityFork v17 (zygisk Build/property spoofing for GMS DroidGuard)
- Installer removes conflicting standalone modules (TrickyStore, PIF, USNF, MHPC, etc.)
- Bootloader / verified-boot prop spoofing in `post-fs-data.sh`
- Late OEM-specific prop spoofing in `service.sh` (Samsung, Realme, OnePlus, Xiaomi, Oppo)
- Action button refreshes fingerprint via `autopif4` and restarts PI processes via `killpi`
- Optional keybox auto-fetch (`keybox_fetch.sh`) — set `KEYBOX_URL` to any raw HTTPS URL
- Daemon classpath renamed to `tee_classes.dex` so PIF zygisk's `classes.dex` lookup doesn't collide
- `build.sh` / `build.ps1` download pinned upstream release ZIPs and repackage — rebuild on any upstream release by bumping the version variables
