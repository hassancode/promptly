"""
Citation Service

Handles citation validation, URL checking, and citation-related operations.
"""
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import httpx
from enum import Enum

from ..models.ai_response import Citation
from ..core.logging import get_logger

logger = get_logger(__name__)


class CitationValidity(str, Enum):
    """Citation validity status"""
    VALID = "valid"
    BROKEN = "broken"
    SUSPICIOUS = "suspicious"
    UNKNOWN = "unknown"


async def check_url_validity(
    url: str,
    timeout: int = 5,
    verify_ssl: bool = True,
) -> Tuple[CitationValidity, Optional[str]]:
    """
    Check if a URL is valid and accessible.

    Args:
        url: URL to check
        timeout: Request timeout in seconds (default: 5)
        verify_ssl: Whether to verify SSL certificates (default: True)

    Returns:
        Tuple of (CitationValidity, error_message)
    """
    try:
        # Parse URL
        parsed = urlparse(url)

        # Basic validation
        if not parsed.scheme in ["http", "https"]:
            return CitationValidity.SUSPICIOUS, "Invalid URL scheme"

        if not parsed.netloc:
            return CitationValidity.SUSPICIOUS, "Missing domain"

        # Check for common suspicious patterns
        suspicious_patterns = [
            r"\.tk$",  # Free TLD often used for spam
            r"bit\.ly",  # URL shorteners (can be legit but suspicious for citations)
            r"tinyurl",
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IP addresses
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, parsed.netloc, re.IGNORECASE):
                return CitationValidity.SUSPICIOUS, "Suspicious domain pattern"

        # Make HEAD request to check accessibility
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            try:
                response = await client.head(url, timeout=timeout, follow_redirects=True)

                if response.status_code >= 200 and response.status_code < 300:
                    return CitationValidity.VALID, None
                elif response.status_code >= 400 and response.status_code < 500:
                    return CitationValidity.BROKEN, f"HTTP {response.status_code}"
                elif response.status_code >= 500:
                    return CitationValidity.BROKEN, f"Server error {response.status_code}"
                else:
                    return CitationValidity.UNKNOWN, f"Unexpected status {response.status_code}"

            except httpx.TimeoutException:
                # Timeout doesn't necessarily mean broken, could be slow
                return CitationValidity.UNKNOWN, "Request timeout"
            except httpx.RequestError as e:
                return CitationValidity.BROKEN, f"Request failed: {str(e)}"

    except Exception as e:
        logger.error(f"Error checking URL validity: {url}", extra={"error": str(e)})
        return CitationValidity.UNKNOWN, f"Validation error: {str(e)}"


async def validate_citations(
    citations: List[Citation],
    check_urls: bool = True,
) -> Dict[str, CitationValidity]:
    """
    Validate a list of citations.

    Args:
        citations: List of Citation objects
        check_urls: Whether to perform URL accessibility checks (default: True)

    Returns:
        Dict mapping citation ID to CitationValidity
    """
    validity_map = {}

    for citation in citations:
        if not check_urls:
            # Just do basic validation
            if citation.url and urlparse(citation.url).scheme in ["http", "https"]:
                validity_map[citation.id] = CitationValidity.VALID
            else:
                validity_map[citation.id] = CitationValidity.SUSPICIOUS
        else:
            # Full URL check
            validity, _ = await check_url_validity(citation.url)
            validity_map[citation.id] = validity

    return validity_map


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain string or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def categorize_citation_source(url: str) -> str:
    """
    Categorize citation source by domain.

    Args:
        url: Citation URL

    Returns:
        Category string (e.g., "official", "news", "social", "academic", "other")
    """
    domain = extract_domain(url)
    if not domain:
        return "unknown"

    domain_lower = domain.lower()

    # Official/company websites
    official_patterns = [
        r"\.com$", r"\.io$", r"\.co$", r"\.net$", r"\.org$"
    ]

    # News sites
    news_domains = [
        "nytimes.com", "wsj.com", "reuters.com", "bloomberg.com",
        "techcrunch.com", "theverge.com", "wired.com", "bbc.com",
        "cnn.com", "forbes.com"
    ]

    # Social media
    social_domains = [
        "twitter.com", "x.com", "facebook.com", "linkedin.com",
        "instagram.com", "youtube.com", "reddit.com"
    ]

    # Academic
    academic_patterns = [
        r"\.edu$", r"\.ac\.", r"arxiv\.org", r"scholar\.google",
        r"researchgate\.net", r"ieee\.org", r"acm\.org"
    ]

    # Check categories
    if any(domain_lower in d for d in news_domains):
        return "news"

    if any(domain_lower in d for d in social_domains):
        return "social"

    for pattern in academic_patterns:
        if re.search(pattern, domain_lower):
            return "academic"

    # Default to official/company
    return "official"


def score_citation_quality(
    citation: Citation,
    validity: CitationValidity = CitationValidity.UNKNOWN,
) -> int:
    """
    Score citation quality on a scale of 0-100.

    Factors:
    - URL validity (40 points)
    - Has title (20 points)
    - Has snippet (20 points)
    - Source category (20 points: academic=20, news=15, official=10, social=5)

    Args:
        citation: Citation object
        validity: CitationValidity enum value

    Returns:
        Quality score (0-100)
    """
    score = 0

    # URL validity (40 points)
    validity_scores = {
        CitationValidity.VALID: 40,
        CitationValidity.UNKNOWN: 20,
        CitationValidity.SUSPICIOUS: 10,
        CitationValidity.BROKEN: 0,
    }
    score += validity_scores.get(validity, 0)

    # Has title (20 points)
    if citation.title:
        score += 20

    # Has snippet (20 points)
    if citation.snippet:
        score += 20

    # Source category (20 points)
    category = categorize_citation_source(citation.url)
    category_scores = {
        "academic": 20,
        "news": 15,
        "official": 10,
        "social": 5,
        "unknown": 0,
    }
    score += category_scores.get(category, 0)

    return min(score, 100)
