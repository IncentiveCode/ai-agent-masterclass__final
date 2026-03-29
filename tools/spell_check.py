from langchain_core.tools import tool
from config import OPENAI_API_KEY

@tool
def spell_check(text: str) -> str:
	"""
	한국어 텍스트의 맞춤법, 띄어쓰기, 문법 오류를 찾아서
  교정된 텍스트를 반환한다. 수정된 부분은 【】로 표시한다.
	"""

	from langchain.chat_models import init_chat_model
	checker = init_chat_model("openai:gpt-4o-mini")
	response = checker.invoke(f"""
		다음 텍스트의 맞춤법, 띄어쓰기, 문법 오류를 교정하세요.
		수정된 부분은 【수정된 단어】로 표시하세요.
		원본 의미는 절대 변경하지 마세요.

		텍스트:
		{text}
	"""
	)

	return response.content