from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from config import TAVILY_API_KEY

tavily_search = TavilySearch(max_results=3)


@tool
def search_trending(query: str) -> str:
	"""
	주어진 주제에 대한 최신 트렌드, 키워드, 관련 정보를 웹에서 검색한다.
  SEO 키워드 제안이나 최신 동향 확인에 사용한다.
	"""

	try:
		results = tavily_search.invoke(query)

		if not results:
			return "검색 결과가 없습니다."
		
		formatted = []
		for r in results:
			formatted.append(
				f"- {r.get('content', '')[:200]}\n"
				f"  출처: {r.get('url', '')}"
			)
		
		return "\n\n".join(formatted)
	except Exception as e:
		return f"검색 실패: {str(e)}"