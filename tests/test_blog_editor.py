import pytest
from my_nodes.blog_editor import blog_editor

test_state = {
	"original_text": """LangGraph는 LangChain팀이 만든 프래임워크입니다.
그래프 기반으로 AI 에이전트를 설게할 수 있어요.
State, Node, Edge 세가지가 핵심 구성요소 입니다.""",
	"tone": "technical",
	"feedback": "",
	"proofread_text": "",
}

result = blog_editor(test_state)
print("=== 교정 결과 ===")
print(result["proofread_text"])
print(f"\n도구 호출 횟수: {len([m for m in result['messages'] if hasattr(m, 'tool_calls') and m.tool_calls])}")


# pytest 테스트.
class TestBlogEditor:
	""" blog_editor 노드 테스트 """

	@pytest.fixture
	def base_state(self):
		return {
			"original_text": """LangGraph는 LangChain팀이 만든 프래임워크입니다.
그래프 기반으로 AI 에이전트를 설게할 수 있어요.
State, Node, Edge 세가지가 핵심 구성요소 입니다.""",
			"tone": "technical",
			"feedback": "",
			"proofread_text": "",
		}


	def test_returns_proofread_text(self, base_state):
		""" 교정된 텍스트가 반환되어야 한다. """
		result = blog_editor(base_state)

		assert "proofread_text" in result
		assert len(result["proofread_text"]) > 0


	def test_feedback_is_cleared(self, base_state):
		"""교정 후 feedback은 빈 문자열로 초기화"""
		base_state["feedback"] = "이전 피드백"
		result = blog_editor(base_state)

		assert result["feedback"] == ""


	def test_messages_are_returned(self, base_state):
		"""에이전트 실행 이력(messages)이 반환되어야 한다"""
		result = blog_editor(base_state)

		assert "messages" in result
		assert len(result["messages"]) >= 2  # 최소 user + ai


	def test_spelling_is_corrected(self, base_state):
		"""명백한 오탈자가 교정되어야 한다"""
		result = blog_editor(base_state)

		assert "프래임워크" not in result["proofread_text"]
		assert "설게" not in result["proofread_text"]


	def test_respects_feedback(self):
		"""피드백이 있으면 교정에 반영되어야 한다"""
		state = {
			"original_text": "AI 에이전트는 매우 좋습니다.",
			"tone": "casual",
			"feedback": "좀 더 구체적인 예시를 추가해주세요",
		}
		result = blog_editor(state)

		assert len(result["proofread_text"]) > len(state["original_text"])