# JTO 0.2 integration scope

- Report-only delivery: HWPX/HWP contains source metadata, uncertainty and input-check scope as * notes. Optional PDF is the same report rendered by auto-hwp. No sources.md, validation.json or ZIP deliverable.
- Internal approval/report voice: advisory and polite sentence endings rejected. Host AI revises to ~함/~임/~예정. Unconfirmed facts remain unconfirmed.
- auto-hwp Apache-2.0: pinned d96d1f2f40458dc3d4470392524dcda9e43ac304, CLI server-side PDF export. The supplied HWP/HWPX is retained; PDF uses an independent engine and fallback fonts, not native Hancom validation. Build/install and live-render verification are distinct.
- paper-verify https://github.com/chrisryugj/paper-verify is a Claude Code skill, not a hosted MCP server. No license was present in the inspected repository tree. Its code/text is not redistributed. JTO provides an independently implemented Crossref DOI metadata tool and requires host-AI original-source review. This is not the complete paper-verify legal/KCI/RISS/page-verification feature set.
- hangul-spellchecker https://gitlab.aigov.go.kr/jhoh9505/hangul-spellchecker is an offline HTML/Electron application, not an MCP service. Its own-code redistribution license was not found in README/package.json/repository tree; third-party notices license dependencies only. JTO uses Debian Hunspell + Korean dictionary instead, without copying the application's proprietary-status custom rules. Spelling output is suggestions, never automatic edits. Public-language, privacy and sentence-agreement rules from the app are not included.
- Hunspell and dictionary notices are installed with Debian packages under /usr/share/doc. Auto-hwp LICENSE/NOTICE and font license files are retained in container.
- These boundaries must be stated to operators. Do not call all three upstream projects fully integrated.

## Verification

Run pytest. Inspect notes' original HWPX char styles (1200 units, 중고딕) and the additional 12pt HWP char shape. Do not silently remove sources to force a 1-page output. The conservative text budget includes notes; actual page count and native typography need rendering.
