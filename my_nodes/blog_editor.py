from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from tools.spell_check import spell_check
from tools.search import search_trending
from state import State
from config import OPENAI_API_KEY

tools = [spell_check, search_trending]

llm = init_chat_model("openai:gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

blog_editor_prompt = """당신은 기술 블로그 전문 에디터입니다.

## 역할
사용자가 작성한 글을 기술 블로그에 적합하도록 교정하고 다듬습니다.

## 작업 순서
1. 먼저 spell_check 도구로 맞춤법을 검사하세요.
  - 글이 500자를 넘으면 단락별로 나눠서 여러 번 호출하세요.
2. 필요하다면 search_trending 도구로 관련 키워드나 최신 트렌드를 확인하세요.
3. 아래 기준으로 글을 교정하세요:
  - 오탈자 및 맞춤법 수정
  - 문장 흐름과 논리 구조 개선
  - 기술 용어의 정확성 확인
  - SEO를 위한 키워드 자연스럽게 배치
4. 마지막으로 블로그에 바로 업로드를 할 수 있도록, SEO 측면에서 한번 더 검토하고 문장의 배치를 정리하세요.

## 톤 가이드: {tone}
아래 톤에 맞게 문체를 반드시 변환하세요:
- technical: 정확한 기술 용어 사용, 객관적 서술, ~합니다 체
- casual: 친근한 대화체, ~해요 체, 독자에게 말을 거는 느낌
- professional: 비즈니스 톤, 간결하고 신뢰감 있는 서술

중요: 원본과 톤이 다르면, 원본의 의미는 유지하되 문체는 반드시 변환하세요.
원본과 동일한 글을 반환하지 마세요.

## 출력 형식
교정된 전체 글을 반환하세요. 
수정한 부분은 설명하지 않아도 됩니다.
교정이 완료된 최종 글만 출력하세요.

## 피드백
{feedback}
"""

# ----- 서브 그래프 -----
def call_llm(state: State):
	"""
	LLM을 호출한다. (도구 호출 요청 또는 최종 답변)
	"""

	response = llm_with_tools.invoke(state["messages"])
	return {"messages": [response]}


def should_continue(state: State):
	"""
	LLM 응답에 tool_calls가 있으면 도구 실행, 없으면 종료
	"""

	last_message = state["messages"][-1]
	if getattr(last_message, "tool_calls", None):
		return "tools"
	return END


def build_blog_agent():
	"""
	blog_editor 용 에이전트 서브그래프
	"""

	graph = StateGraph(State)

	graph.add_node("call_llm", call_llm)
	graph.add_node("tools", ToolNode(tools))

	graph.add_edge(START, "call_llm")
	graph.add_conditional_edges("call_llm", should_continue)
	graph.add_edge("tools", "call_llm")

	return graph.compile()

blog_agent = build_blog_agent()


# ----- 메인 그래프 -----
def blog_editor(state: State):
	tone = state.get("tone", "technical")
	feedback = state.get("feedback", "")
	original_text = state.get("original_text", "")

	print(f"[blog_editor] tone: {tone}")
	print(f"[blog_editor] original_text: {original_text[:100]}")

	prompt = blog_editor_prompt.format(
		tone=tone,
		feedback=f"사용자가 이전 교정에 대해 다음과 같이 요청했습니다: {feedback}"
			if feedback 
			else "없음 (첫 교정입니다)",
	)

	response = blog_agent.invoke({
		"messages": [
			SystemMessage(content=prompt),
			{"role": "user", "content": original_text},
		]
	})
	# print('response:', response)

	# 최종 교정글 추출
	final_text = ""
	for msg in reversed(response["messages"]):
		if getattr(msg, "type", "") == "ai" and msg.content:
			final_text = msg.content
			break;

	print(f"[blog_editor] proofread_text: {final_text[:100]}")
	print(f"[blog_editor] 동일 여부: {original_text.strip() == final_text.strip()}")
	
	return {
		"proofread_text": final_text, # or original_text,
		"feedback": "",
    "messages": response["messages"],
  }