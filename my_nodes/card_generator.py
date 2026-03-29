import json
from langchain.chat_models import init_chat_model
from state import State
from config import OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4o-mini")

card_generator_prompt = """당신은 SNS 카드뉴스 기획 전문가입니다.

## 역할
교정된 글을 4~5장의 카드뉴스로 구조화합니다.
각 카드는 독립적으로 읽혀도 이해할 수 있으면서,
전체를 이어서 보면 하나의 스토리가 되어야 합니다.

## 카드 구성 원칙
	- 카드 1: 후킹 — 관심을 끄는 질문이나 강렬한 한 줄
	- 카드 2~3: 핵심 내용 전달
	- 카드 4: 정리 또는 요약
	- 카드 5 (선택): CTA(Call to Action) — 팔로우, 저장, 링크 안내 등

## 플랫폼: {platform}
	- instagram: 카드당 텍스트 3~4줄 이내, 해시태그는 마지막 카드에
	- linkedin: 카드당 텍스트 4~5줄, 데이터나 인사이트 강조
	- threads: 카드당 1~2줄, 대화체

## 톤 가이드: {tone}

## 응답 형식
반드시 아래 JSON 배열만 반환하세요. 다른 텍스트는 포함하지 마세요.

[
	{{
		"card_number": 1,
		"title": "카드 제목 (짧고 강렬하게)",
		"body": "카드 본문 내용",
		"highlight": "강조할 핵심 문구 (1줄)",
		"type": "hook"
	}},
	{{
		"card_number": 2,
		"title": "두 번째 카드 제목",
		"body": "본문 내용",
		"highlight": "강조 문구",
		"type": "content"
	}}
]

type은 hook, content, summary, cta 중 하나입니다.

## 피드백
{feedback}

## 교정된 글
{proofread_text}
"""

def card_generator(state: State):
	platform = state.get("platform", "instagram")
	tone = state.get("tone", "casual")
	feedback = state.get("feedback", "")
	proofread_text = state.get("proofread_text", "")

	prompt = card_generator_prompt.format(
		platform=platform,
		tone=tone,
		feedback=f"사용자가 이전 카드에 대해 다음과 같이 요청했습니다: {feedback}"
			if feedback
			else "없음 (첫 생성입니다)",
		proofread_text=proofread_text,
	)
	response = llm.invoke(prompt)

	try:
		# JSON 파싱 (```json 블록 제거 처리)
		content = response.content.strip()
		content = content.removeprefix("```json").removesuffix("```").strip()
		cards = json.loads(content)

		# 검증..
		if not isinstance(cards, list) or len(cards) == 0:
			raise ValueError("빈 카드 리스트")

		for i, card in enumerate(cards):
			card.setdefault("card_number", i + 1)
			card.setdefault("title", "")
			card.setdefault("body", "")
			card.setdefault("highlight", "")
			card.setdefault("type", "content")

		return {
			"cards": cards,
			"feedback": "",
		}
		
	except (json.JSONDecodeError, KeyError, ValueError) as e:
		print(f"[card_generator] 파싱 실패: {e}")
		print(f"[card_generator] 원본 응답: {response.content[:300]}")

		# 파싱 실패 시 기본 카드 1장 생성
		return {
			"cards": [{
				"card_number": 1,
				"title": "카드 생성 실패",
				"body": proofread_text[:200],
				"highlight": "수동 확인이 필요합니다",
				"type": "content",
			}],
			"feedback": "",
		}

