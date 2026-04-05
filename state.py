from typing import Annotated, Literal
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages

class State(MessagesState):
	# google sheets info
	row_id: str
	title: str
	original_text: str
	type: Literal[
		"blog", "sns", "slide", "all",
	]
	platform: str
	tone: str

	# 교정 정보
	proofread_text: str
	feedback: str 

	# self review
	review_score: int
	review_feedback: str 
	retry_count: int

	# card news
	cards: list[dict]

	# output
	output_paths: list[str]

	# streamlit chat_input 사용 여부
	chat_input: bool