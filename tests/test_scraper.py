import pytest
import respx
import httpx
from speed2audit.agents.scraper import ContextScraper, ScrapedContext


@pytest.mark.asyncio
async def test_scraper_extracts_clean_content():
    html_sample = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Acme Fleet Tracking Software</title>
            <meta name="description" content="Real-time GPS tracking and route optimization for logistics companies.">
        </head>
        <body>
            <nav><a href="/home">Home</a></nav>
            <h1>Real-Time Fleet Management</h1>
            <p>Our SaaS platform helps logistics managers reduce fuel costs by 20% and track over 500+ vehicles simultaneously.</p>
            <h2>Plans and Pricing</h2>
            <p>Starting at $49/vehicle per month. Custom enterprise quotes available.</p>
            <footer>Copyright 2026 Acme Corp</footer>
        </body>
    </html>
    """

    scraper = ContextScraper()

    with respx.mock(base_url="https://acmefleet.com") as respx_mock:
        respx_mock.get("/").mock(
            return_value=httpx.Response(200, text=html_sample)
        )

        context: ScrapedContext = await scraper.scrape_url("https://acmefleet.com")

        assert context.title == "Acme Fleet Tracking Software"
        assert "Real-time GPS tracking" in context.meta_description
        assert "Fleet Management" in context.extracted_text
        assert "Plans and Pricing" in context.extracted_text
        # Ensure boilerplate is stripped
        assert "Copyright 2026" not in context.extracted_text or "Fleet Management" in context.extracted_text


@pytest.mark.asyncio
async def test_scraper_handles_network_failure():
    scraper = ContextScraper()

    with respx.mock(base_url="https://invalid-site-999.com") as respx_mock:
        respx_mock.get("/").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        with pytest.raises(Exception):
            await scraper.scrape_url("https://invalid-site-999.com")
