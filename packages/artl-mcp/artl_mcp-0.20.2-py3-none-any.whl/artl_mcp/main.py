import asyncio
import sys
from importlib import metadata

import click
from fastmcp import FastMCP

from artl_mcp.client import run_client
from artl_mcp.tools import (
    clean_text,
    doi_to_pmid,
    # PubMed utilities tools
    extract_doi_from_url,
    extract_pdf_text,
    get_abstract_from_pubmed_id,
    # DOIFetcher-based tools
    get_doi_fetcher_metadata,
    # Original tools
    get_doi_metadata,
    get_doi_text,
    get_full_text_from_bioc,
    get_full_text_from_doi,
    get_full_text_info,
    get_pmcid_text,
    get_pmid_from_pmcid,
    get_pmid_text,
    get_text_from_pdf_url,
    get_unpaywall_info,
    pmid_to_doi,
    # Search tools
    search_papers_by_keyword,
    search_pubmed_for_pmids,
    search_recent_papers,
)

try:
    __version__ = metadata.version("artl-mcp")
except metadata.PackageNotFoundError:
    __version__ = "unknown"


def create_mcp():
    """Create the FastMCP server instance and register tools."""
    mcp = FastMCP(
        "artl-mcp",
        instructions="""
All Roads to Literature (ARtL) MCP provides tools for retrieving scientific literature
metadata, full text, and abstracts via DOI, PMID, or PMCID.

## Supported Identifiers
- **DOI**: Digital Object Identifier (e.g., "10.1038/nature12373")
- **PMID**: PubMed ID (e.g., "23851394")
- **PMCID**: PubMed Central ID (e.g., "PMC3737249")
- **Keywords**: Natural language search terms

This server offers three main categories of functionality:

## 1. Literature Search and Discovery
- **search_papers_by_keyword**: Search article metadata via keywords
- **search_recent_papers**: Find recent publications for specific keywords or topics
- **search_pubmed_for_pmids**: Search PubMed for articles using keywords and return
PMIDs with metadata

## 2. Metadata and Abstract Retrieval
- **get_doi_metadata**: Get comprehensive metadata for papers using DOI
- **get_abstract_from_pubmed_id**: Retrieve abstracts from PubMed using PMID
- **get_doi_fetcher_metadata**: Enhanced metadata retrieval with email requirement
- **get_unpaywall_info**: Check open access availability via Unpaywall

## 3. Full Text Access and Processing
- **get_full_text_from_doi**: Retrieve full text content using DOI (requires email)
- **get_full_text_info**: Get detailed full text availability information
- **get_text_from_pdf_url**: Extract text content from PDF URLs
- **extract_pdf_text**: Standalone PDF text extraction
- **get_pmcid_text**: Get full text from PubMed Central ID
- **get_pmid_text**: Get full text using PMID
- **get_full_text_from_bioc**: Retrieve full text in BioC format
- **clean_text**: Clean and format extracted text content

## 4. Identifier Conversion and Utilities
- **extract_doi_from_url**: Extract DOI from various URL formats
- **doi_to_pmid**: Convert DOI to PMID
- **pmid_to_doi**: Convert PMID to DOI
- **get_pmid_from_pmcid**: Get PMID from PMC ID
- **get_doi_text**: Direct text retrieval using DOI

## Usage Notes
- Many tools require an email address for API access (CrossRef, Unpaywall policies)
- Tools automatically handle identifier cleaning and format conversion
- Rate limiting and proper headers are implemented for respectful API usage
- All tools return structured data or None on failure for easy error handling

""",
    )

    # Register all tools
    # Original tools
    mcp.tool(get_doi_metadata)
    mcp.tool(get_abstract_from_pubmed_id)

    # DOIFetcher-based tools (require email)
    mcp.tool(get_doi_fetcher_metadata)
    mcp.tool(get_unpaywall_info)
    mcp.tool(get_full_text_from_doi)
    mcp.tool(get_full_text_info)
    mcp.tool(get_text_from_pdf_url)
    mcp.tool(clean_text)

    # Standalone tools
    mcp.tool(extract_pdf_text)

    # PubMed utilities tools
    mcp.tool(extract_doi_from_url)
    mcp.tool(doi_to_pmid)
    mcp.tool(pmid_to_doi)
    mcp.tool(get_doi_text)
    mcp.tool(get_pmid_from_pmcid)
    mcp.tool(get_pmcid_text)
    mcp.tool(get_pmid_text)
    mcp.tool(get_full_text_from_bioc)
    mcp.tool(search_pubmed_for_pmids)

    # Search tools
    mcp.tool(search_papers_by_keyword)
    mcp.tool(search_recent_papers)

    return mcp


# Server instance
mcp = create_mcp()


@click.command()
@click.option("--doi-query", type=str, help="Run a direct query (DOI string).")
@click.option("--pmid-search", type=str, help="Search PubMed for PMIDs using keywords.")
@click.option(
    "--max-results",
    type=int,
    default=20,
    help="Maximum number of results to return (default: 20).",
)
def cli(doi_query, pmid_search, max_results):
    """
    Run All Roads to Literature MCP server (default) or CLI tools.

    CLI Options:
        --doi-query: Run a direct query using a DOI string.
        --pmid-search: Search PubMed for PMIDs using keywords.
        --max-results: Maximum number of results to return (default: 20).

    Default Behavior:
        If no options are provided, the MCP server runs over stdio.
    """
    # Validate mutual exclusion of CLI options
    if doi_query and pmid_search:
        raise click.ClickException(
            "Error: Cannot use both --doi-query and --pmid-search simultaneously. "
            "Please use only one option at a time."
        )

    if doi_query:
        # Run the client in asyncio
        asyncio.run(run_client(doi_query, mcp))
    elif pmid_search:
        # Run PubMed search directly
        result = search_pubmed_for_pmids(pmid_search, max_results)
        if result and result["pmids"]:
            print(
                f"Found {result['returned_count']} PMIDs out of "
                f"{result['total_count']} total results for query '{pmid_search}':"
            )
            for pmid in result["pmids"]:
                print(f"  {pmid}")
            if result["total_count"] > result["returned_count"]:
                max_possible = min(result["total_count"], 100)
                print(f"\nTo get more results, use: --max-results {max_possible}")
        elif result:
            print(f"No PMIDs found for query '{pmid_search}'")
        else:
            print(f"Error searching for query '{pmid_search}'")
    else:
        # Default behavior: Run the MCP server over stdio
        mcp.run()


def main():
    """Main entry point for the application."""
    if "--version" in sys.argv:
        print(__version__)
        sys.exit(0)
    cli()


if __name__ == "__main__":
    main()
