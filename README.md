# zamr · Android Modules Repository

Eine kuratierte Sammlung von Root-Modulen für **Magisk**, **KernelSU**, **APatch** und **MMRL**.

## MMRL hinzufügen

In MMRL unter **Repositories → Hinzufügen** diese Basis-URL eintragen:

```text
https://zelect0r.github.io/zamr/
```

Nicht `repo.json` oder `json/modules.json` eintragen – MMRL lädt den Modulindex automatisch von dort.

## Kategorien

| Kategorie | Inhalt |
| --- | --- |
| Apps | YouTube Morphe, Music Morphe |
| Customization | iOS Emoji |
| Integrity | Play Integrity Fix/Fork, TEESimulator, Tricky Addons |
| KernelSU | SUSFS for KernelSU |
| Root Hide | Zygisk Assistant |
| Utility | zygisk-detach |
| Xposed | Vector |
| Zygisk | Zygisk Next, NeoZygisk, ReZygisk |
| WebUI | Tricky Addon-Module |

## Enthaltene Module

16 Module werden über den MMRL-Index veröffentlicht:

- Zygisk Next, NeoZygisk, ReZygisk
- Zygisk Assistant und zygisk-detach
- Play Integrity Fix und Play Integrity Fork
- TEESimulator und TEESimulator-RS
- Tricky Addon Enhanced und Tricky Addon Target List
- SUSFS for KernelSU
- Vector
- iOS Emoji
- YouTube Morphe und Music Morphe

Der vollständige Index ist unter [`json/modules.json`](json/modules.json) verfügbar.

## Aktualisierungen

GitHub Actions prüft alle sechs Stunden die neuesten GitHub-Releases. Neue ZIPs werden übernommen, der MMRL-Index wird neu erzeugt und automatisch veröffentlicht. Dadurch kann es nach einem Upstream-Release einige Minuten dauern, bis die Version in MMRL sichtbar ist.

## Voraussetzungen

- Android 8 oder neuer (je nach Modul)
- kompatibler Root-Manager: Magisk, KernelSU oder APatch
- unterstützte Architektur und Android-API des jeweiligen Moduls beachten

## Sicherheit

Root-Module verändern Systemverhalten. Vor jeder Installation ein vollständiges Backup erstellen und die Hinweise des jeweiligen Projekts lesen. Nutzung auf eigene Verantwortung.

## Lizenz

Die Lizenz kann je Modul abweichen und steht in den jeweiligen `track.json`- und Modulmetadaten. Repository-Metadaten stehen unter Apache-2.0, sofern nicht anders angegeben.

## Links

- [MMRL-Repository](https://zelect0r.github.io/zamr/)
- [Modulindex](json/modules.json)
- [GitHub Issues](https://github.com/zelect0r/zamr/issues)
