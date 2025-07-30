"""
Pickaxe OpenAlex MCP Server

A Model Context Protocol (MCP) server that provides access to the OpenAlex API
"""

from typing import Any, List, Dict
from pyalex import Authors, Institutions, Works
from fastmcp import FastMCP

mcp = FastMCP(
    name="open-alex",
    instructions="You are a research assistant that can search for academic papers, authors, and their details using the Semantic Scholar API. You can also retrieve citations and references for specific papers.",
)

@mcp.tool()
async def search_institutions(query: str, page: int = 0, per_page: int = 10) -> List[Dict[str, Any]]:
    """
    Search for institutions by name.

    Args:
        query: Name of the institution to search for
        page: Page number for pagination (default is 0)
        per_page: Number of results per page (default is 10)

    Returns:
        List of institutions matching the search criteria
    """
    return Institutions().search(query).paginate(page=page, per_page=per_page)

@mcp.tool()
async def search_authors(query: str, page: int = 0, per_page: int = 10) -> List[Dict[str, Any]]:
    """
    Search for authors by name.

    Args:
        query: Name of the author to search for
        page: Page number for pagination (default is 0)
        per_page: Number of results per page (default is 10)

    Returns:
        List of authors matching the search criteria
    """
    return Authors().search(query).filter(page=page, per_page=per_page)

@mcp.tool()
async def search_works(query: str, page: int = 0, per_page: int = 10) -> List[Dict[str, Any]]:
    """
    Search for works (papers) by title or keywords.

    Args:
        query: Title or keywords of the work to search for
        page: Page number for pagination (default is 0)
        per_page: Number of results per page (default is 10)

    Returns:
        List of works matching the search criteria
    """
    return Works().search(query).filter(page=page, per_page=per_page)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
