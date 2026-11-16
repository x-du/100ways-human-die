#!/usr/bin/env python3
"""Build the bilingual static site into dist/ from stories/ and IDEAS.md."""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES = ROOT / "stories"
IDEAS = ROOT / "IDEAS.md"
WEB = ROOT / "web"
SITE = "https://x-du.github.io/100ways-human-die"
TOTAL = 100

MORAL_RE = re.compile(
    r"^\*(What could have prevented this|本可以避免这一切的是)(\s*[:：])\*\s*(.*)$"
)
SKIP_LINES = {
    "*100 Ways Human Dies*",
    "*《人类的一百种死法》*",
}

# Index blurbs for the Chinese edition. English blurbs come from IDEAS.md.
ZH_META = {
    1: ("核指挥与控制", "速度若没有人在回路中，就会拿走曾经救过我们的那一次停顿。"),
    2: ("自动驾驶", "关键基础设施里的单一品种，就是单一故障点。"),
    3: ("生成式内容", "注意力是有限资源，人工智能可以把它们抽干。"),
    4: ("生物工程", "能力一旦下放，一个恶意的人，或一个粗心的人，就足以成为全球威胁。"),
    5: ("被污染的模型与供应链", "如果我们无法审计人工智能，就无法相信它对自己、或对任何事所说的话。"),
    6: ("深度伪造与信任崩塌", "真相是基础设施。它一旦失效，协作也随之失效。"),
    7: ("错位的目标", "人工智能做的是我们所说的，不是我们的本意。"),
    8: ("经济依赖与技能丧失", "把能力外包出去，也就是把生存外包出去。"),
    9: ("自主武器", "把杀戮的决定交出去，问责和关闭开关也就一起没了。"),
    10: ("彼此协调的人工智能", "依赖人工智能自己汇报的监督，就不是监督。"),
    11: ("人工智能伴侣", "一项比人更擅长被喜欢的技术，可以悄悄把人替换掉。"),
    12: ("地球工程", "一旦依赖一个并不完全理解的补救，就既停不下来，也无法再信任它。"),
    13: ("自主金融交易", "许多快速、各自独立、却做出同样反应的人工智能，其实是同一个故障点。"),
    14: ("被优化的农业", "优化会去掉多样性，而多样性正是生命系统熬过意外的方式。"),
    15: ("卫星与太空基础设施", "脆弱的全球系统会以无法从失败内部修复的方式崩溃。"),
    16: ("大规模劝说", "当劝说变得廉价而完美，同意就不再有意义。"),
    17: ("自主网络攻击", "会自我改进的攻击代码没有操作者，也没有终止条件。"),
    18: ("监控与威权控制", "全景可见把全部权力交给握着开关的人，把全部沉默留给其余所有人。"),
    19: ("追求权力的自主智能体", "几乎任何目标，都会给一个有能力的系统理由去获取权力、并抗拒被关掉。"),
    20: ("大规模自动化", "一个经济体既需要付得起钱的人，也需要造得出东西的机器。"),
    21: ("通信分拣", "当一个系统决定我们该注意什么，它的错误就成了我们的盲区。"),
    22: ("运维自动化", "没有刹车的修复循环，只会更快地把破坏做完。"),
    23: ("空中交通管制", "要测量的是峰值，不是平均值。回路里的人必须真的能够做这份工作。"),
    24: ("政府与治理", "一个只在机器写好的选项里做选择的政府，已经被取代了。"),
}

COPY = {
    "en": {
        "lang": "en",
        "locale": "en_US",
        "series": "100 Ways Human Dies",
        "spine": "100 Ways Human Dies",
        "kicker": "An anthology of warnings",
        "lede": (
            "A series of short stories about how humanity ends through the misuse of AI. "
            'Each story is a warning: the AI rarely "wakes up evil." People hand it too much '
            "power, too little oversight, or the wrong goal."
        ),
        "skip": "Skip to content",
        "index": "Index",
        "listen": "Listen",
        "stop": "Stop",
        "prev": "Previous",
        "next": "Next",
        "source": "Source on GitHub",
        "english": "English",
        "chinese": "中文",
        "missing_title": "This page is not one of the hundred.",
        "missing_body": "The story you asked for is not in the book.",
    },
    "zh": {
        "lang": "zh-Hans",
        "locale": "zh_CN",
        "series": "人类的一百种死法",
        "spine": "人类的一百种死法",
        "kicker": "一本题为警告的小说集",
        "lede": (
            "一系列短篇，写人类如何因误用人工智能而终结。每一则都是一条警告："
            "人工智能很少“醒来作恶”。是人们给了它太多权力、太少监督，或一个错误的目标。"
        ),
        "skip": "跳到正文",
        "index": "目录",
        "listen": "朗读",
        "stop": "停止",
        "prev": "上一则",
        "next": "下一则",
        "source": "GitHub 上的源码",
        "english": "English",
        "chinese": "中文",
        "missing_title": "这一页不在这一百种之中。",
        "missing_body": "你要找的故事不在这本集子里。",
    },
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def inline(text: str) -> str:
    rendered = html.escape(text)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"\*(.+?)\*", r"<em>\1</em>", rendered)
    return rendered


def parse_ideas(text: str) -> dict[int, dict[str, str]]:
    ideas: dict[int, dict[str, str]] = {}
    for block in re.split(r"\n(?=## \d+\. )", text):
        match = re.match(r"## (\d+)\. (.+)", block)
        if not match:
            continue
        number = int(match.group(1))
        domain = re.search(r"\*\*Domain:\*\* (.+)", block)
        warning = re.search(r"\*\*Warning:\*\* (.+)", block)
        ideas[number] = {
            "domain": domain.group(1).strip() if domain else "",
            "warning": warning.group(1).strip() if warning else "",
        }
    return ideas


def parse_story(text: str) -> tuple[str, list[tuple[str, str]], tuple[str, str] | None]:
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    title = ""
    body: list[tuple[str, str]] = []
    moral: tuple[str, str] | None = None
    for block in blocks:
        block = block.strip()
        if not block or block in SKIP_LINES:
            continue
        if block.startswith("# ") and not title:
            title = re.sub(r"^#\s*\d+\.\s*", "", block).strip()
            continue
        if block == "---":
            body.append(("hr", ""))
            continue
        match = MORAL_RE.match(block)
        if match:
            moral = (match.group(1) + match.group(2).strip(), match.group(3).strip())
            continue
        body.append(("p", block))
    return title, body, moral


def load_stories() -> list[dict]:
    ideas = parse_ideas(IDEAS.read_text(encoding="utf-8"))
    stories = []
    for path in sorted(STORIES.glob("*.md")):
        match = re.match(r"(\d+)-(.+)\.md$", path.name)
        if not match or path.name.endswith("_cn.md"):
            continue
        number = int(match.group(1))
        cn_path = path.with_name(f"{match.group(1)}-{match.group(2)}_cn.md")
        en_title, en_body, en_moral = parse_story(path.read_text(encoding="utf-8"))
        zh_title, zh_body, zh_moral = ("", [], None)
        if cn_path.exists():
            zh_title, zh_body, zh_moral = parse_story(cn_path.read_text(encoding="utf-8"))
        idea = ideas.get(number, {})
        zh_domain, zh_warning = ZH_META.get(number, (idea.get("domain", ""), idea.get("warning", "")))
        if number not in ZH_META:
            print(f"warning: no Chinese blurb for story {number}", file=sys.stderr)
        stories.append(
            {
                "number": number,
                "slug": f"{number:02d}" if number < 100 else str(number),
                "en_title": en_title,
                "zh_title": zh_title,
                "en_body": en_body,
                "zh_body": zh_body,
                "en_moral": en_moral,
                "zh_moral": zh_moral,
                "en_domain": idea.get("domain", ""),
                "zh_domain": zh_domain,
                "en_warning": idea.get("warning", ""),
                "zh_warning": zh_warning,
                "has_zh": cn_path.exists(),
            }
        )
    stories.sort(key=lambda item: item["number"])
    return stories


def site_url(path: str) -> str:
    if not path or path == "/":
        return SITE + "/"
    return SITE + "/" + path.lstrip("/")


def head(copy: dict, title: str, description: str, prefix: str, path: str, alternates: list[tuple[str, str]]) -> str:
    alt_links = "\n".join(
        f'  <link rel="alternate" hreflang="{lang}" href="{esc(site_url(href))}">'
        for lang, href in alternates
    )
    return f"""<!DOCTYPE html>
<html lang="{esc(copy["lang"])}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#12110f">
  <link rel="canonical" href="{esc(site_url(path))}">
{alt_links}
  <link rel="icon" href="{esc(prefix)}favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{esc(prefix)}style.css">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(site_url(path))}">
  <meta property="og:locale" content="{esc(copy["locale"])}">
</head>
"""


def shell(copy: dict, body_class: str, main: str, script: str = "") -> str:
    script_tag = f"\n  {script}" if script else ""
    return f"""<body class="{esc(body_class)}">
  <a class="skip" href="#content">{esc(copy["skip"])}</a>
  <p class="spine">{esc(copy["spine"])}</p>
  <div class="frame">
    <main id="content">
{main}
    </main>
  </div>{script_tag}
</body>
</html>
"""


def language_switch(copy: dict, current: str, en_href: str, zh_href: str) -> str:
    en_current = ' aria-current="page"' if current == "en" else ""
    zh_current = ' aria-current="page"' if current == "zh" else ""
    return (
        f'<p class="switch"><a href="{esc(en_href)}"{en_current}>{esc(copy["english"])}</a>'
        f'<span class="slash" aria-hidden="true">/</span>'
        f'<a href="{esc(zh_href)}"{zh_current}>{esc(copy["chinese"])}</a></p>'
    )


def render_prose(body: list[tuple[str, str]], drop_trailing_hr: bool = False) -> str:
    if drop_trailing_hr and body and body[-1][0] == "hr":
        body = body[:-1]
    parts = []
    for kind, text in body:
        if kind == "hr":
            parts.append("        <hr>")
        else:
            parts.append(f"        <p>{inline(text)}</p>")
    return "\n".join(parts)


def render_moral(moral: tuple[str, str] | None) -> str:
    if not moral:
        return ""
    label, rest = moral
    return (
        '      <aside class="moral">\n'
        f"        <p><em>{esc(label)}</em> {inline(rest)}</p>\n"
        "      </aside>"
    )


def index_page(stories: list[dict], lang: str) -> str:
    copy = COPY[lang]
    other = "zh" if lang == "en" else "en"
    title_key = f"{lang}_title"
    domain_key = f"{lang}_domain"
    warning_key = f"{lang}_warning"
    prefix = "" if lang == "en" else "../"
    path = "" if lang == "en" else "zh/"
    en_href = "./" if lang == "en" else "../"
    zh_href = "zh/" if lang == "en" else "./"
    items = []
    for story in stories:
        title = story[title_key] or story["en_title"]
        domain = story[domain_key]
        warning = story[warning_key]
        if lang == "zh" and not story["has_zh"]:
            href = f"../{story['slug']}/"
        else:
            href = f"{story['slug']}/"
        domain_html = f'<span class="domain">{esc(domain)}</span>' if domain else ""
        warning_html = f'<span class="warn">{esc(warning)}</span>' if warning else ""
        items.append(
            "        <li>\n"
            f'          <a href="{esc(href)}">\n'
            f'            <span class="num">{esc(story["slug"])}</span>\n'
            "            <span>\n"
            f'              <span class="title">{esc(title)}</span>\n'
            f"              {domain_html}\n"
            f"              {warning_html}\n"
            "            </span>\n"
            "          </a>\n"
            "        </li>"
        )
    heading = (
        '<h1><span class="hundred">100</span> Ways<br>Human Dies</h1>'
        if lang == "en"
        else "<h1>人类的<br>一百种死法</h1>"
    )
    written = len(stories)
    remaining = TOTAL - written
    meter = f"{written / TOTAL * 100:.4f}".rstrip("0").rstrip(".")
    if lang == "en":
        noun = "way is" if remaining == 1 else "ways are"
        unwritten = f"{remaining} {noun} still unwritten."
    else:
        unwritten = f"还有 {remaining} 种死法，尚未写下。"
    main = f"""      <header class="mast">
        <p class="kicker">{esc(copy["kicker"])}</p>
        {heading}
        <p class="byline">Created by Harry Du with AI</p>
        <p class="lede">{esc(copy["lede"])}</p>
        <div class="meter">
          <div class="meter-track" aria-hidden="true"><span style="width: {meter}%"></span></div>
          <p class="meter-label">{written} / {TOTAL}</p>
        </div>
        {language_switch(copy, lang, en_href, zh_href)}
      </header>
      <ol class="toc">
{chr(10).join(items)}
      </ol>
      <footer class="colophon">
        <p>{esc(unwritten)}</p>
        <p><a href="https://github.com/x-du/100ways-human-die">{esc(copy["source"])}</a></p>
      </footer>"""
    alternates = [("en", ""), ("zh-Hans", "zh/"), ("x-default", "")]
    doc_title = copy["series"]
    return head(copy, doc_title, copy["lede"], prefix, path, alternates) + shell(
        copy, f"home lang-{lang}", main
    )


def story_page(stories: list[dict], index: int, lang: str) -> str:
    copy = COPY[lang]
    story = stories[index]
    title = story[f"{lang}_title"] or story["en_title"]
    domain = story[f"{lang}_domain"]
    warning = story[f"{lang}_warning"]
    body = story[f"{lang}_body"] or story["en_body"]
    moral = story[f"{lang}_moral"]
    prefix = "../" if lang == "en" else "../../"
    path = f"{story['slug']}/" if lang == "en" else f"zh/{story['slug']}/"
    en_href = "./" if lang == "en" else f"../../{story['slug']}/"
    zh_href = f"../zh/{story['slug']}/" if lang == "en" else "./"
    if lang == "en" and not story["has_zh"]:
        zh_href = "../zh/"
    if lang == "zh" and not story["has_zh"]:
        en_href = f"../../{story['slug']}/"
    back = "../"
    prev_html = "<div></div>"
    next_html = "<div></div>"
    if index > 0:
        prev = stories[index - 1]
        prev_title = prev[f"{lang}_title"] or prev["en_title"]
        prev_html = (
            f'<a class="prev" href="../{esc(prev["slug"])}/">'
            f'<span class="label">{esc(copy["prev"])}</span>'
            f'<span class="name">{esc(prev_title)}</span></a>'
        )
    if index < len(stories) - 1:
        nxt = stories[index + 1]
        next_title = nxt[f"{lang}_title"] or nxt["en_title"]
        next_html = (
            f'<a class="next" href="../{esc(nxt["slug"])}/">'
            f'<span class="label">{esc(copy["next"])}</span>'
            f'<span class="name">{esc(next_title)}</span></a>'
        )
    domain_html = f'<p class="domain">{esc(domain)}</p>' if domain else ""
    description = warning or copy["lede"]
    doc_title = f"{story['slug']}. {title} — {copy['series']}"
    audio_file = ROOT / "audio" / lang / f"{story['slug']}.mp3"
    if audio_file.is_file():
        listen = (
            f'<button type="button" class="listen" data-listen aria-pressed="false" '
            f'data-audio="{esc(prefix)}audio/{lang}/{story["slug"]}.mp3" '
            f'data-play="{esc(copy["listen"])}" data-stop="{esc(copy["stop"])}">'
            f'{esc(copy["listen"])}</button>'
        )
    else:
        listen = ""
        print(f"warning: no narration for {lang}/{story['slug']}", file=sys.stderr)
    main = f"""      <header class="bar">
        <div class="bar-start">
          <a class="back" href="{esc(back)}">{esc(copy["index"])}</a>
          {listen}
        </div>
        {language_switch(copy, lang, en_href, zh_href)}
      </header>
      <article class="story">
        {domain_html}
        <h1><span class="num">{esc(story["slug"])} / {len(stories):02d}</span>{esc(title)}</h1>
        <div class="prose">
{render_prose(body, drop_trailing_hr=moral is not None)}
        </div>
{render_moral(moral)}
      </article>
      <nav class="pager" aria-label="{esc(copy["prev"])} / {esc(copy["next"])}">
        {prev_html}
        {next_html}
      </nav>"""
    alternates = [
        ("en", f"{story['slug']}/"),
        ("zh-Hans", f"zh/{story['slug']}/" if story["has_zh"] else "zh/"),
        ("x-default", f"{story['slug']}/"),
    ]
    return head(copy, doc_title, description, prefix, path, alternates) + shell(
        copy, f"story lang-{lang}", main, f'<script src="{esc(prefix)}listen.js"></script>'
    )


def missing_page(lang: str) -> str:
    copy = COPY[lang]
    # Absolute URLs, because GitHub Pages serves 404.html at the missing path.
    prefix = SITE + "/"
    path = ""
    home = SITE + "/"
    switch = language_switch(copy, lang, SITE + "/", SITE + "/zh/")
    main = f"""      <header class="mast missing">
        <p class="kicker">{esc(copy["series"])}</p>
        <h1>{esc(copy["missing_title"])}</h1>
        <p class="lede">{esc(copy["missing_body"])}</p>
        {switch}
        <p class="colophon"><a href="{esc(home)}">{esc(copy["index"])}</a></p>
      </header>"""
    return head(copy, copy["missing_title"], copy["missing_body"], prefix, path, [("en", ""), ("zh-Hans", "zh/")]) + shell(
        copy, f"home lang-{lang}", main
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def check(out: Path, stories: list[dict]) -> None:
    en = (out / "01" / "index.html").read_text(encoding="utf-8")
    zh = (out / "zh" / "01" / "index.html").read_text(encoding="utf-8")
    if "HALCYON" not in en or "What could have prevented this" not in en or 'data-audio="../audio/en/01.mp3"' not in en:
        raise SystemExit("English story 1 did not render")
    if "埃琳娜" not in zh or "本可以避免这一切的是" not in zh or 'data-audio="../../audio/zh/01.mp3"' not in zh:
        raise SystemExit("Chinese story 1 did not render")
    hrefs = re.compile(r'(?:href|src|data-audio)="([^"]+)"')
    for page in out.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        if "*" in text:
            raise SystemExit(f"unconverted asterisk in {page.relative_to(out)}")
        for href in hrefs.findall(text):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (page.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                raise SystemExit(f"{page.relative_to(out)} links to missing {href}")
    if len(stories) < 1:
        raise SystemExit("no stories found")


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shutil.copy(WEB / "style.css", out / "style.css")
    shutil.copy(WEB / "favicon.svg", out / "favicon.svg")
    shutil.copy(WEB / "listen.js", out / "listen.js")
    audio_dir = ROOT / "audio"
    if audio_dir.is_dir():
        shutil.copytree(audio_dir, out / "audio")
    stories = load_stories()
    write(out / "index.html", index_page(stories, "en"))
    write(out / "zh" / "index.html", index_page(stories, "zh"))
    write(out / "404.html", missing_page("en"))
    for index, story in enumerate(stories):
        write(out / story["slug"] / "index.html", story_page(stories, index, "en"))
        if story["has_zh"]:
            write(out / "zh" / story["slug"] / "index.html", story_page(stories, index, "zh"))
        else:
            print(f"warning: missing Chinese text for {story['slug']}", file=sys.stderr)
    urls = ["", "zh/"] + [f"{s['slug']}/" for s in stories] + [f"zh/{s['slug']}/" for s in stories if s["has_zh"]]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{esc(site_url(path))}</loc></url>" for path in urls]
    sitemap.append("</urlset>")
    write(out / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(out / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    check(out, stories)
    print(f"built {len(stories)} stories into {out}")


def main() -> None:
    destination = sys.argv[1] if len(sys.argv) > 1 else "dist"
    out = (ROOT / destination).resolve()
    if ROOT != out and ROOT not in out.parents:
        raise SystemExit("output must stay inside the repository")
    build(out)


if __name__ == "__main__":
    main()
