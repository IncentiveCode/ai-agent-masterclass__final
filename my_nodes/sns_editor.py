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

sns_editor_prompt = """당신은 SNS 콘텐츠 전문 에디터입니다.

## 역할
사용자가 작성한 글을 SNS 카드뉴스에 적합하도록 교정하고 다듬습니다.
원본의 핵심 메시지를 유지하면서, 짧고 강렬하게 재구성하세요.

## 작업 순서
1. 먼저 spell_check 도구로 맞춤법을 검사하세요.
  - 글이 500자를 넘으면 단락별로 나눠서 여러 번 호출하세요.
2. 필요하다면 search_trending 도구로 관련 해시태그나 트렌드를 확인하세요.
3. 아래 기준으로 글을 교정하세요:
  - 오탈자 및 맞춤법 수정
  - 긴 문장을 짧고 리듬감 있게 분리
  - 핵심 키워드와 강조 포인트 명확하게
  - 불필요한 수식어 제거

## 플랫폼: {platform}
플랫폼 특성에 맞게 문체를 조정하세요:
	- instagram: 친근하고 캐주얼한 톤, 해시태그 활용
	- linkedin: 전문적이고 신뢰감 있는 톤, 인사이트 중심
	- threads: 대화체, 짧은 문장, 의견 중심

## 톤 가이드: {tone}

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

def build_sns_agent():
	"""
	sns_editor 용 에이전트 서브그래프
	"""

	graph = StateGraph(State)

	graph.add_node("call_llm", call_llm)
	graph.add_node("tools", ToolNode(tools))

	graph.add_edge(START, "call_llm")
	graph.add_conditional_edges("call_llm", should_continue)
	graph.add_edge("tools", "call_llm")

	return graph.compile()

sns_agent = build_sns_agent()


# ----- 메인 그래프 -----
def sns_editor(state: State):
	platform = state.get("platform", "instagram")
	tone = state.get("tone", "casual")
	feedback = state.get("feedback", "")
	original_text = state.get("original_text", "")

	prompt = sns_editor_prompt.format(
		platform=platform,
		tone=tone,
		feedback=f"사용자가 이전 교정에 대해 다음과 같이 요청했습니다: {feedback}"
			if feedback 
			else "없음 (첫 교정입니다)",
	)

	response = sns_agent.invoke({
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
	
	return {
		"proofread_text": final_text or original_text,
		"feedback": "",
    "messages": response["messages"],
  }