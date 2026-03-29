from my_nodes.self_review import self_review

test_state = {
	"original_text": "LangGraph는 LangChain팀이 만든 프래임워크입니다.",
	"proofread_text": "LangGraph는 LangChain 팀이 만든 프레임워크입니다.",
	"tone": "technical",
	"retry_count": 0,
}

result = self_review(test_state)
print(f"점수: {result['review_score']}")
print(f"피드백: {result['review_feedback']}")
print(f"재시도 횟수: {result['retry_count']}")