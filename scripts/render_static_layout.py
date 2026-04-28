from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "templates"
THOUGHT_PIECES_PATH = REPO_ROOT / "data" / "thought-pieces.json"

ROOT_ACTIVE_BY_PAGE = {
    "thought-pieces.html": "thought_pieces",
    "brain-dumps.html": "brain_dumps",
    "data.html": "data",
    "reporting.html": "reporting",
    "about.html": "about",
}

HEADER_START = "<!-- site-header:start -->"
HEADER_END = "<!-- site-header:end -->"
FOOTER_START = "<!-- site-footer:start -->"
FOOTER_END = "<!-- site-footer:end -->"
ARTICLE_NAV_START = "<!-- article-navigation:start -->"
ARTICLE_NAV_END = "<!-- article-navigation:end -->"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    if path.read_text(encoding="utf-8") == text:
        return False

    path.write_text(text, encoding="utf-8")
    return True


def render_template(name: str, values: dict[str, str]) -> str:
    output = read_text(TEMPLATE_DIR / name).strip()

    for key, value in values.items():
        output = output.replace(f"{{{{{key}}}}}", value)

    return output


def page_prefix(path: Path) -> str:
    return "../" if path.parent.name == "articles" else ""


def active_section(path: Path) -> str | None:
    if path.parent.name == "articles":
        return "thought_pieces"

    return ROOT_ACTIVE_BY_PAGE.get(path.name)


def template_values(path: Path) -> dict[str, str]:
    active = active_section(path)
    values = {
        "prefix": page_prefix(path),
        "thought_pieces_active": "",
        "brain_dumps_active": "",
        "data_active": "",
        "reporting_active": "",
        "about_active": "",
    }

    if active:
        values[f"{active}_active"] = " active"

    return values


def replace_marked_or_first(pattern: str, text: str, start: str, end: str, replacement: str) -> str:
    marked = re.compile(
        rf"\n*{re.escape(start)}.*?{re.escape(end)}",
        flags=re.DOTALL,
    )

    block = f"\n{start}\n{replacement}\n{end}"

    if marked.search(text):
        return marked.sub(block, text, count=1)

    return re.sub(pattern, block, text, count=1, flags=re.DOTALL)


def discover_pages() -> list[Path]:
    root_pages = sorted(REPO_ROOT.glob("*.html"))
    article_pages = sorted((REPO_ROOT / "articles").glob("*.html"))
    return [*root_pages, *article_pages]


def load_articles() -> list[dict[str, object]]:
    payload = json.loads(read_text(THOUGHT_PIECES_PATH))
    articles = payload.get("articles", [])

    for article in articles:
        article["_date"] = date.fromisoformat(str(article["date"]))

    return articles


def article_by_path(articles: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        str(article["link"]): article
        for article in articles
        if str(article.get("link", "")).startswith("articles/")
    }


def article_href_for_current_page(target_link: str) -> str:
    if target_link.startswith("articles/"):
        return target_link.removeprefix("articles/")

    return f"../{target_link}"


def escape_html(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def sibling_articles(current: dict[str, object], articles: list[dict[str, object]]) -> tuple[dict[str, object] | None, dict[str, object] | None]:
    same_section = sorted(
        [
            article
            for article in articles
            if article.get("section") == current.get("section")
            and str(article.get("link", "")).startswith("articles/")
        ],
        key=lambda article: (article["_date"], str(article["title"])),
    )
    current_index = next(
        index
        for index, article in enumerate(same_section)
        if article["link"] == current["link"]
    )

    previous_article = same_section[current_index - 1] if current_index > 0 else None
    next_article = same_section[current_index + 1] if current_index + 1 < len(same_section) else None
    return previous_article, next_article


def related_articles(current: dict[str, object], articles: list[dict[str, object]]) -> list[dict[str, object]]:
    candidates = [
        article
        for article in articles
        if article.get("link") != current.get("link")
        and article.get("section") == current.get("section")
        and str(article.get("link", "")).startswith("articles/")
    ]

    current_date = current["_date"]

    def related_sort_key(article: dict[str, object]) -> tuple[int, int, str]:
        topic_match = article.get("topic") == current.get("topic")
        date_distance = abs((article["_date"] - current_date).days)
        return (0 if topic_match else 1, date_distance, str(article["title"]))

    return sorted(candidates, key=related_sort_key)[:2]


def navigation_card(article: dict[str, object], label: str) -> str:
    href = article_href_for_current_page(str(article["link"]))
    title = escape_html(article["title"])
    return (
        f'      <a class="article-navigation-card" href="{href}">\n'
        f'        <span class="article-navigation-label">{label}</span>\n'
        f'        <span>{title}</span>\n'
        f"      </a>"
    )


def render_article_navigation(current: dict[str, object], articles: list[dict[str, object]]) -> str:
    previous_article, next_article = sibling_articles(current, articles)
    cards = []

    if previous_article:
        cards.append(navigation_card(previous_article, "Previous"))

    if next_article:
        cards.append(navigation_card(next_article, "Next"))

    related_links = [
        f'        <li><a href="{article_href_for_current_page(str(article["link"]))}">{escape_html(article["title"])}</a></li>'
        for article in related_articles(current, articles)
    ]

    grid = "\n".join(cards) if cards else '      <p class="article-navigation-empty">No adjacent articles in this section yet.</p>'
    related = "\n".join(related_links) if related_links else "        <li>No related articles yet.</li>"

    return f"""<nav class="article-navigation" aria-label="Article navigation">
  <a class="article-navigation-back" href="../thought-pieces.html">Back to Thought Pieces</a>
  <div class="article-navigation-grid">
{grid}
  </div>
  <div class="article-navigation-related">
    <p class="article-navigation-label">Related</p>
    <ul>
{related}
    </ul>
  </div>
</nav>"""


def replace_article_navigation(text: str, path: Path, articles: list[dict[str, object]]) -> str:
    link = f"articles/{path.name}"
    current = article_by_path(articles).get(link)
    marked = re.compile(
        rf"\n*\s*{re.escape(ARTICLE_NAV_START)}.*?{re.escape(ARTICLE_NAV_END)}\s*",
        flags=re.DOTALL,
    )

    if not current:
        return marked.sub("", text, count=1)

    block = (
        f"      {ARTICLE_NAV_START}\n"
        f"{render_article_navigation(current, articles)}\n"
        f"      {ARTICLE_NAV_END}\n"
    )

    if marked.search(text):
        return marked.sub(f"\n{block}", text, count=1)

    return re.sub(r"(\n\s*</article>\s*\n\s*</main>)", f"\n{block}\\1", text, count=1)


def render_page(path: Path, articles: list[dict[str, object]]) -> bool:
    text = read_text(path)
    values = template_values(path)
    header = render_template("site-header.html", values)
    footer = render_template("site-footer.html", values)

    text = replace_marked_or_first(
        r"\s*<header class=\"site-header\">.*?</header>",
        text,
        HEADER_START,
        HEADER_END,
        header,
    )
    text = replace_marked_or_first(
        r"\s*<footer class=\"site-footer\">.*?</footer>",
        text,
        FOOTER_START,
        FOOTER_END,
        footer,
    )

    if path.parent.name == "articles":
        text = replace_article_navigation(text, path, articles)

    return write_if_changed(path, text)


def main() -> None:
    articles = load_articles()
    changed = []

    for page in discover_pages():
        if render_page(page, articles):
            changed.append(page.relative_to(REPO_ROOT).as_posix())

    if changed:
        print("Updated static layout:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Static layout already up to date.")


if __name__ == "__main__":
    main()
