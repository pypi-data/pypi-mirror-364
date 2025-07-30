"""
Pickaxe Semantic Scholar MCP Server

A Model Context Protocol (MCP) server that provides access to the Semantic Scholar API
"""

from typing import Any, List, Dict
from semanticscholar import SemanticScholar
from fastmcp import FastMCP

mcp = FastMCP(
    name="semantic-scholar",
    instructions="You are a Semantic Scholar API client. Call search_papers() to find relevant papers based on the user's query.",
)

sch = SemanticScholar()

@mcp.tool()
async def search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for papers on Semantic Scholar using a query string.

    Args:
        query: Search query string
        limit: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing paper information
    """
    results = sch.search_paper(query, limit=limit)

    return [
        {
            "paperId": paper.paperId,
            "title": paper.title,
            "abstract": paper.abstract,
            "year": paper.year,
            "authors": [{"name": author.name, "authorId": author.authorId} for author in paper.authors],
            "url": paper.url,
            "venue": paper.venue,
            "publicationTypes": paper.publicationTypes,
            "citationCount": paper.citationCount
        } for paper in results
    ]

@mcp.tool()
async def get_paper_details(paper_id: str) -> Dict[str, Any]:
    """
    Get details of a specific paper on Semantic Scholar.

    Args:
        paper_id: ID of the paper

    Returns:
        Dictionary containing paper details
    """
    return sch.get_paper(paper_id)

@mcp.tool()
async def get_author_details(author_id: str) -> Dict[str, Any]:
    """
    Get details of a specific author on Semantic Scholar.

    Args:
        author_id: ID of the author

    Returns:
        Dictionary containing author details
    """
    return sch.get_author(author_id)

@mcp.tool()
async def get_citations_and_references(paper_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get citations and references for a specific paper on Semantic Scholar.

    Args:
        paper_id: ID of the paper

    Returns:
        Dictionary containing lists of citations and references
    """
    paper = sch.get_paper(paper_id)

    return {
        "citations": [
            {
                "paperId": citation.paperId,
                "title": citation.title,
                "year": citation.year,
                "authors": [{"name": author.name, "authorId": author.authorId} for author in citation.authors]
            } for citation in paper["citations"]
        ],
        "references": [
            {
                "paperId": reference.paperId,
                "title": reference.title,
                "year": reference.year,
                "authors": [{"name": author.name, "authorId": author.authorId} for author in reference.authors]
            } for reference in paper["references"]
        ]
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
