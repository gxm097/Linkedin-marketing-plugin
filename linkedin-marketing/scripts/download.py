# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Download Canva's exported slides into a numbered folder.

Usage:
    uv run --script download.py <out_dir> <url> [<url> ...]

URLs are saved in the order given, as ``01.png``, ``02.png``, ... — slide order
is argument order, which is also what build_pdf.py sorts on.

This replaces a `curl -fsSL "<url>" -o slides/01.png` loop. Windows 10+ does
ship `curl.exe`, but in Windows PowerShell 5.1 `curl` is an **alias for
`Invoke-WebRequest`**, which accepts neither `-fsSL` nor `-o`, so the loop fails
there with an error about a parameter rather than about the download. urllib is
in the standard library, so this costs no dependency and behaves the same
everywhere.

Canva's export URLs expire 24 hours after the export job finishes, so a 403 or
404 here usually means a run was interrupted and the export has to be redone,
not that anything is misconfigured. The message says so.
"""

import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

#: Canva serves exports over https. Anything else is a mistake worth refusing
#: rather than following: a file:// or data: URL here would read local disk.
_SCHEMES = {"https"}

_TIMEOUT = 60
_UA = "linkedin-marketing-plugin (+https://github.com/gxm097/linkedin-marketing-plugin)"


def fetch(url: str, out: Path) -> int:
    scheme = urlparse(url).scheme.lower()
    if scheme not in _SCHEMES:
        sys.exit(f"Refusing a {scheme or 'scheme-less'} URL; expected https: {url}")

    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:
            payload = response.read()
    except urllib.error.HTTPError as error:
        expired = " — Canva export URLs expire after 24 hours; re-export" if error.code in (403, 404) else ""
        sys.exit(f"{url}\n  HTTP {error.code} {error.reason}{expired}")
    except (urllib.error.URLError, TimeoutError) as error:
        sys.exit(f"{url}\n  {error}")

    if not payload:
        sys.exit(f"{url}\n  returned an empty body")

    out.write_bytes(payload)
    return len(payload)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(
            f"Usage: uv run --script {Path(__file__).name} <out_dir> <url> [<url> ...]"
        )

    out_dir = Path(sys.argv[1])
    urls = sys.argv[2:]
    out_dir.mkdir(parents=True, exist_ok=True)

    # Zero-padded to the width the count needs, so ten or more slides still sort
    # in slide order rather than 1, 10, 2.
    width = max(2, len(str(len(urls))))
    for index, url in enumerate(urls, start=1):
        out = out_dir / f"{index:0{width}d}.png"
        size = fetch(url, out)
        print(f"{out}: {size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
