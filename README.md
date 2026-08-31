# zelect0r's Android Modules Repository

A curated collection of root modules for **Magisk**, **KernelSU**, **APatch**, and **MMRL**.

## Add to MMRL

In MMRL, open **Repositories → Add** and enter this base URL:

```text
https://zelect0r.github.io/zamr/
```

Do not enter `repo.json` or `json/modules.json`; MMRL loads the module index from the base URL automatically.

## Categories

| Category | Modules |
| --- | --- |
| Apps | YouTube Morphe, Music Morphe |
| Customization | iOS Emoji |
| Integrity | Play Integrity Fix, Play Integrity Fork, TEESimulator, TEESimulator-RS, Tricky Addon Enhanced, Tricky Addon Target List |
| KernelSU | SUSFS for KernelSU, Hybrid Mount |
| Root Hide | Zygisk Assistant, HMA-OSS Zygisk |
| Utility | zygisk-detach, bindhosts, MSD, DT2W Fix |
| Xposed | Vector |
| Zygisk | Zygisk Next, NeoZygisk, ReZygisk |
| WebUI | Tricky Addon Enhanced, Tricky Addon Target List |

## Included modules

The MMRL index currently publishes 21 modules:

- Zygisk Next, NeoZygisk, and ReZygisk
- Zygisk Assistant and zygisk-detach
- Play Integrity Fix and Play Integrity Fork
- TEESimulator and TEESimulator-RS
- Tricky Addon Enhanced and Tricky Addon Target List
- SUSFS for KernelSU
- Vector
- iOS Emoji
- YouTube Morphe and Music Morphe
- HMA-OSS Zygisk
- Hybrid Mount
- bindhosts
- DT2W Fix
- MSD

The complete index is available at [`json/modules.json`](json/modules.json).

## Automatic updates

GitHub Actions checks for new upstream GitHub releases every hour. The MMRL index and each module's update metadata are rebuilt automatically. After an upstream release, it can take a few minutes before the new version appears in MMRL and on the repository page.

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
