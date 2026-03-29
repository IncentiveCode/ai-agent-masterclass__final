from typing import Literal

from langgraph.graph import END
from state import State

def route_by_type(
	state: State,
) -> Literal["blog_editor", "sns_editor", "slide_generator"]:
	"""
	type 에 따라 node 분기
	"""

	type_map = {
		"blog": "blog_editor",
		"sns": "sns_editor",
		"slide": "slide_generator",
		"all": "blog_editor",
	}

	type = state.get("type", "")
	if type not in type_map:
		raise ValueError(
			f"알 수 없는 type: '{type}'."
			f"허용값: {list(type_map.keys())}"
		)

	return type_map[type]


# blog, sns 용으로 나눠서 사용. 추후엔 합칠 예정.
def after_self_review(state: State) -> str:
	"""
	self_review 점수에 따라 재교정 또는 사용자의 검토 단계로 분기
	이미 교정 과정을 3번 했다면 강제로 통과
	"""
	
	score = state.get("review_score", 0)
	retry_count = state.get("retry_count", 0)

	if score >= 7 or retry_count >= 3:
		return "review"
	else:
		return "editor"


def after_blog_save(state: State) -> str:
	"""
	all type 처리. blog 완료 후 sns로 분기
	"""

	if state.get("type", "") == "all":
		return "sns_editor"
	return END


def after_blog_review(state: State) -> str:
	"""
	after_self_review 의 blog 버전.
	"""

	score = state.get("review_score", 0)
	retry_count = state.get("retry_count", 0)

	if score >= 7 or retry_count >= 3:
		return "review_blog"
	else:
		return "blog_editor"

	
def after_sns_review(state: State) -> str:
	"""
	after_self_review 의 sns 버전.
	"""

	score = state.get("review_score", 0)
	retry_count = state.get("retry_count", 0)

	if score >= 7 or retry_count >= 3:
		return "card_generator"
	else:
		return "sns_editor"