import re
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel


class ScrapedContext(BaseModel):
    url: str
    title: str
    meta_description: str
    extracted_text: str


class ContextScraper:
    """Extracts business context, value proposition, and offerings from a website URL."""

    def __init__(self, timeout_seconds: float = 15.0):
        self.timeout = timeout_seconds
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    async def scrape_url(self, url: str) -> ScrapedContext:
        """Fetch and extract clean structured text from the target website."""
        async with httpx.AsyncClient(
            timeout=self.timeout, headers=self.headers, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or soup.find(
            "meta", attrs={"property": re.compile(r"og:description", re.I)}
        )
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # Remove irrelevant tags
        for element in soup(["script", "style", "noscript", "svg", "header", "nav", "footer", "iframe"]):
            element.decompose()

        # Extract text blocks
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Truncate to reasonable context window limit (e.g. ~8000 characters)
        if len(clean_text) > 8000:
            clean_text = clean_text[:8000] + "\n...[Content truncated]..."

        return ScrapedContext(
            url=url,
            title=title,
            meta_description=meta_desc,
            extracted_text=clean_text,
        )
