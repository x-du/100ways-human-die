#!/usr/bin/env python3
"""Pre-generate human narration for each story with neural voices.

English uses en-US-AndrewNeural. Chinese uses zh-CN-YunyangNeural.
Both are adult narrators. Existing files are left in place unless --force is set.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site  # noqa: E402

ROOT = build_site.ROOT
AUDIO = ROOT / "audio"
VOICES = {
    "en": "en-US-AndrewNeural",
    "zh": "zh-CN-YunyangNeural",
}
RATE = "-4%"


def plain(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def narration(story: dict, lang: str) -> str:
    title = story[f"{lang}_title"] or story["en_title"]
    body = story[f"{lang}_body"] or story["en_body"]
    moral = story[f"{lang}_moral"]
    parts = [plain(title)]
    for kind, text in body:
        if kind == "p":
            spoken = plain(text)
            if spoken:
                parts.append(spoken)
    if moral:
        parts.append(plain(f"{moral[0]} {moral[1]}"))
    return "\n\n".join(parts)


def stale(dest: Path, sources: list[Path], force: bool) -> bool:
    if force or not dest.is_file() or dest.stat().st_size < 1000:
        return True
    newest = max(path.stat().st_mtime for path in sources)
    return newest > dest.stat().st_mtime


async def synthesize(text: str, voice: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_suffix(".part.mp3")
    if temporary.exists():
        temporary.unlink()
    await edge_tts.Communicate(text, voice, rate=RATE).save(str(temporary))
    if temporary.stat().st_size < 1000:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"recording too small: {dest.name}")
    temporary.replace(dest)


async def one(story: dict, lang: str, force: bool, semaphore: asyncio.Semaphore) -> str:
    slug = story["slug"]
    if lang == "zh" and not story["has_zh"]:
        return f"skip {lang}/{slug}"
    sources = story_sources(story, lang)
    dest = AUDIO / lang / f"{slug}.mp3"
    if not stale(dest, sources, force):
        return f"kept {lang}/{slug}"
    text = narration(story, lang)
    async with semaphore:
        print(f"recording {lang}/{slug} ({len(text)} chars)", flush=True)
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                await synthesize(text, VOICES[lang], dest)
                return f"wrote {lang}/{slug}"
            except Exception as exc:  # network voices sometimes drop a socket
                last_error = exc
                print(f"retry {lang}/{slug}: {exc}", flush=True)
                await asyncio.sleep(3 * (attempt + 1))
        return f"FAILED {lang}/{slug}: {last_error}"


def story_sources(story: dict, lang: str) -> list[Path]:
    number = story["slug"]
    matches = sorted((ROOT / "stories").glob(f"{number}-*.md"))
    if lang == "en":
        return [path for path in matches if not path.name.endswith("_cn.md")]
    return [path for path in matches if path.name.endswith("_cn.md")]


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate story narration mp3 files.")
    parser.add_argument("--force", action="store_true", help="regenerate even if the mp3 exists")
    parser.add_argument("--only", help="story number, such as 01")
    args = parser.parse_args()
    stories = build_site.load_stories()
    if args.only:
        wanted = args.only.zfill(2)
        stories = [story for story in stories if story["slug"] == wanted]
        if not stories:
            raise SystemExit(f"no story {wanted}")
    semaphore = asyncio.Semaphore(3)
    jobs = [one(story, lang, args.force, semaphore) for story in stories for lang in ("en", "zh")]
    results = await asyncio.gather(*jobs)
    failed = [line for line in results if line.startswith("FAILED")]
    for line in results:
        print(line)
    if failed:
        raise SystemExit(f"{len(failed)} recordings failed")


if __name__ == "__main__":
    asyncio.run(main())
