import json
from langchain.chat_models import init_chat_model
from state import State
from config import OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4o-mini")

review_prompt = """당신은 콘텐츠 품질 검수 전문가입니다.

아래 원본과 교정본을 비교하여 교정 품질을 평가하세요.

## 평가 기준 (각 항목 1~10점)

1. 맞춤법/문법 정확도: 오탈자, 띄어쓰기, 조사 오류가 없는가
2. 문장 자연스러움: 어색한 표현이나 번역투가 없는가
3. 원본 의도 보존: 원본의 핵심 메시지가 유지되었는가
4. 톤 적합성: 요청된 톤({tone})에 맞게 교정되었는가

## 응답 형식
반드시 아래 JSON만 반환하세요. 다른 텍스트는 포함하지 마세요.

{{
    "scores": {{
        "spelling": 8,
        "naturalness": 7,
        "intent": 9,
        "tone": 8
    }},
    "average": 8.0,
    "feedback": "전체적으로 양호하나, 두 번째 문단의 표현이 다소 딱딱합니다."
}}

## 원본
{original}

## 교정본
{proofread}
"""


def self_review(state: State):
	tone = state.get("tone", "")
	original = state.get("original_text", "")
	proofread = state.get("proofread_text", "")

	prompt = review_prompt.format(
		tone=tone,
		original=original,
		proofread=proofread
	)
	response = llm.invoke(prompt)

	try:
		# JSON 파싱 (```json 블록 제거 처리)
		content = response.content.strip()
		content = content.removeprefix("```json").removesuffix("```").strip()
		result = json.loads(content)

		return {
			"review_score": int(result.get("average", 0)),
			"review_feedback": result.get("feedback", ""),
			"retry_count": state.get("retry_count", 0) + 1,
		}
	except (json.JSONDecodeError, KeyError, ValueError):
    # 파싱 실패 시 통과시키되 로그 남기기
		print(f"[self_review] JSON 파싱 실패: {response.content[:200]}")
		return {
			"review_score": 7,  # 파싱 실패 시 통과 처리
			"review_feedback": "자동 평가에 실패했습니다. 수동 확인이 필요합니다.",
		}