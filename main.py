from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import State

# nodes
from my_nodes.fetch_sheets import fetch_from_sheets
from my_nodes.router import route_by_type, after_blog_save, after_blog_review, after_sns_review
from my_nodes.blog_editor import blog_editor
from my_nodes.sns_editor import sns_editor
from my_nodes.self_review import self_review
from my_nodes.review import review_blog, review_cards
from my_nodes.card_generator import card_generator
from my_nodes.render_to_jpg import render_to_jpg
from my_nodes.save_to_sheets import save_to_sheets

graph = StateGraph(State)
graph.add_node("fetch_from_sheets", fetch_from_sheets)

# set node for blog
graph.add_node("blog_editor", blog_editor)
graph.add_node("blog_self_review", self_review)
graph.add_node("review_blog", review_blog)
graph.add_node("blog_save", save_to_sheets)

# set node for sns
graph.add_node("sns_editor", sns_editor)
graph.add_node("sns_self_review", self_review)
graph.add_node("card_generator", card_generator)
graph.add_node("review_cards", review_cards)
graph.add_node("render_to_jpg", render_to_jpg)
graph.add_node("sns_save", save_to_sheets)

# connect edge
# 1. 시작 - 시트 읽기 - 타입별 분기
graph.add_edge(START, "fetch_from_sheets")
graph.add_conditional_edges(
	"fetch_from_sheets",
	route_by_type,
	{
		"blog_editor": "blog_editor",
		"sns_editor": "sns_editor",
	},
)

# 2. blog_editor - self_review - (점수에 따른 분기) - review_blog - save
graph.add_edge("blog_editor", "blog_self_review")
graph.add_conditional_edges(
	"blog_self_review",
	after_blog_review,
	{
		"review_blog": "review_blog",
		"blog_editor": "blog_editor",
	},
)
# review_blog 에서 다른 노드로 연결은 command 를 사용.
graph.add_conditional_edges(
	"blog_save",
	after_blog_save,
	{
		"sns_editor": "sns_editor",
		END: END
	},
)

# #3. sns_editor - self_review - (점수에 따른 분기) - card_generator - review_cards - render_to_jpg - save
graph.add_edge("sns_editor", "sns_self_review")
graph.add_conditional_edges(
	"sns_self_review",
	after_sns_review,
	{
		"card_generator": "card_generator",
		"sns_editor": "sns_editor",
	},
)
graph.add_edge("card_generator", "review_cards")
# review_cards 에서 다른 노드로 연결은 command 를 사용.
graph.add_edge("render_to_jpg", "sns_save")
graph.add_edge("sns_save", END)


# compile
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)