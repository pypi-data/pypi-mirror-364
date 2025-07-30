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
async def search_institutions(name: str) -> List[Dict[str, Any]]:
    """
    Search for institutions by name.

    Args:
        name: Name of the institution to search for

    Returns:
        List of institutions matching the search criteria
    """
    institutions = list(Institutions().search(name).select([
        "id", 
        "display_name", 
        "type", 
        "image_url", 
        "works_count", 
        "cited_by_count", 
        "geo"
    ]).paginate(page=1, per_page=1, n_max=3))

    if len(institutions) > 0:
        institutions = institutions[0]

    return institutions

@mcp.tool()
async def search_authors(name: str) -> List[Dict[str, Any]]:
    """
    Search for authors by name.

    Args:
        name: Name of the author to search for

    Returns:
        List of authors matching the search criteria
    """
    authors = list(Authors().search(name).select([
        "id", 
        "display_name", 
        "works_count", 
        "cited_by_count", 
        "topics"
    ]).paginate(page=1, per_page=1, n_max=3))

    if len(authors) > 0:
        authors = authors[0]
        authors = [{**a, "topics": [{ "id": t["id"], "name": t["display_name"] } for t in a.get("topics", [])]} for a in authors if a is not None]

    return authors

@mcp.tool()
async def search_works(query: str) -> List[Dict[str, Any]]:
    """
    Search for works (papers) by title or keywords.

    Args:
        query: Title or keywords of the work to search for

    Returns:
        List of works matching the search criteria
    """
    works = list(Works().search(query).select([
        "id", 
        "title", 
        "publication_date", 
        "type", 
        "topics",
        "authorships"
    ]).paginate(page=1, per_page=1, n_max=3))

    if len(works) > 0:
        works = works[0]
        works = [{
            **w, 
            "topics": [{ "id": t["id"], "name": t["display_name"] } for t in w.get("topics", [])],
            "authorships": [{ "author_position": t["author_position"], "author": t["author"] } for t in w.get("authorships", [])]
        } for w in works if w is not None]

    return works
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
