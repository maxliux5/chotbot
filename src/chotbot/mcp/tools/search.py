from duckduckgo_search import DDGS

class SearchTool:
    """
    A tool for performing deep searches using DuckDuckGo.
    """

    def run(self, query: str, max_results: int = 3) -> dict:
        """
        Performs a search using DuckDuckGo and returns the results.

        Args:
            query (str): The search query.
            max_results (int): The maximum number of results to return.

        Returns:
            dict: A dictionary containing the search results or an error message.
        """
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=max_results)]
            return {"result": results}
        except Exception as e:
            return {"error": "Search failed", "message": str(e)}
