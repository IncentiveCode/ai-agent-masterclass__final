from langgraph.types import interrupt, Command
from state import State

def review_blog(state: State) -> Command:
	"""
	교정된 블로그 글을 사용자가 직접 확인한다.
	"""

	proofread = state.get("proofread_text", "")
	score = state.get("review_score", 0)
	review_feedback = state.get("review_feedback", "")

	# interrupt
	user_response = interrupt({
		"type": "blog_review",
		"message": "교정된 블로그 글을 확인해주세요.",
		"proofread_text": proofread,
		"self_review": {
			"score": score,
			"feedback": review_feedback,
		},
		"instruction": "승인하려면 'approve', 수정을 원하면 피드백을 입력해주세요.",
	})

	if user_response.strip().lower() == "approve":
		return Command(goto="blog_save")
	else:
		return Command(
			goto="blog_editor",
			update={
				"feedback": user_response,
				"retry_count": 0,
			}
		)


def review_cards(state: State) -> Command:
	"""
	교정된 카드뉴스 내용을 사용자가 직접 확인한다.
	"""

	cards = state.get("cards", [])

	user_response = interrupt({
		"type": "cards_review",
		"message": "카드뉴스 내용을 확인해주세요.",
		"cards": cards,
		"instruction": "승인하려면 'approve', 수정을 원하면 피드백을 입력해주세요.",
	})

	if user_response.strip().lower() == "approve":
		return Command(goto="render_to_jpg")
	else:
		return Command(
			goto="card_generator",
			update={
				"feedback": user_response,
			}
		)