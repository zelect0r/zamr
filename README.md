# zelect0r's Android Modules Repository
![](./assets/banner.webp)

A curated collection of root modules for **Magisk**, **KernelSU**, **APatch**, and **MMRL**.

## Add to MMRL

The repository selection feature has finally been added to MMRL.
Open MMRL, tap "repos", tap "Explore more repos",
scroll down to "zamr", tap on it and add it.

Or manually:

In MMRL, open **Repositories → Add** and enter this base URL:

```text
https://zelect0r.github.io/zamr/
```

Do not enter `repo.json` or `json/modules.json`; MMRL loads the module index from the base URL automatically.

## Categories

| Category | Modules |
| --- | --- |
| Apps | YouTube Morphe, Music Morphe |
| Battery | Frosty, CPU Screen Off |
| Customization | iOS Emoji, LiveBoot |
| Integrity | AlwaysStrong (Fork, Inject, Lite), Integrity Box, Oh My Keymint, Play Integrity Fix, Play Integrity Fork, TEESimulator, TEESimulator-RS, Tricky Addon Enhanced, Tricky Addon Target List, Tricky Store, Tricky Store OSS |
| KernelSU | SUSFS for KernelSU, Hybrid Mount |
| Root Hide | Zygisk Assistant, HMA-OSS Zygisk |
| Utility | zygisk-detach, bindhosts, MSD, DT2W Fix, Android LUKS Mounter, TermuxSu, imgdrive |
| Xposed | Vector |
| Zygisk | Zygisk Next, NeoZygisk, ReZygisk, Meow Zygisk |
| WebUI | Tricky Addon Enhanced, Tricky Addon Target List, Integrity Box |

## Included modules

The MMRL index currently publishes 35 modules:

- Zygisk Next, NeoZygisk, ReZygisk, and Meow Zygisk
- Zygisk Assistant and zygisk-detach
- Play Integrity Fix and Play Integrity Fork
- AlwaysStrong (Fork, Inject, and Lite variants)
- Integrity Box
- Oh My Keymint
- TEESimulator and TEESimulator-RS
- Tricky Addon Enhanced and Tricky Addon Target List
- Tricky Store and Tricky Store OSS
- SUSFS for KernelSU
- Vector
- iOS Emoji
- LiveBoot
- YouTube Morphe and Music Morphe
- HMA-OSS Zygisk
- Hybrid Mount
- bindhosts
- DT2W Fix
- MSD
- Frosty
- CPU Screen Off
- Android LUKS Mounter
- TermuxSu
- imgdrive

The complete index is available at [`json/modules.json`](json/modules.json).

## Automatic updates

GitHub Actions checks for new upstream GitHub releases every hour. The MMRL index and each module's update metadata are rebuilt automatically. After an upstream release, it can take a few minutes before the new version appears in MMRL and on the repository page.

AlwaysStrong is tracked from its GitLab releases. Its three variants are published as separate entries in MMRL — **AlwaysStrong** (PlayIntegrityFork), **AlwaysStrong [Inject]** and **AlwaysStrong [Lite]** (PIF-less) — so you can pick the one that matches your setup. Every published release of each variant is listed in the index, so older builds remain installable instead of being replaced by the newest one.

## Outdated or removed modules

If a module in this repository has been archived, paused, moved to a new upstream, deleted, or is no longer maintained, please report it via [GitHub Issues](https://github.com/zelect0r/zamr/issues) so the index can be updated or the module removed. Pull requests that update the affected `modules/<id>/track.json` are welcome too.

## Support

If you find ZAMR useful and would like to support its development and maintenance, you can support me on Ko-fi.

[☕ Support zelect0r/zamr on Ko-fi](https://ko-fi.com/zelect0r)

Your support helps me continue developing and maintaining ZAMR. Thank you! ❤️

## Requirements

- Android 8 or newer (depending on the module)
- A compatible root manager: Magisk, KernelSU, or APatch
- Check each module's supported architecture and Android API level before installing

## Safety

Root modules modify system behavior. Create a full backup before installation and read the upstream project's notes. Use at your own risk.

## License

Licenses may differ between modules and are listed in their `track.json` and module metadata. Repository metadata is Apache-2.0 unless stated otherwise.

## Links

- [MMRL repository](https://zelect0r.github.io/zamr/)
- [Module index](json/modules.json)
- [GitHub Issues](https://github.com/zelect0r/zamr/issues)
