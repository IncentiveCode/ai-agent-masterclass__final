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