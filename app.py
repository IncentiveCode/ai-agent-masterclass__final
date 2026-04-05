import os
os.system("playwright install")

import streamlit as st
from streamlit_extras.bottom_container import bottom
import json
import time
from pathlib import Path
from langgraph.types import Command
from main import app

st.set_page_config(
	page_title="ContentPilot",
	page_icon="✈️",
	layout="wide",
)


# ----- ----- -----
# 세션 상태 초기화
# ----- ----- -----
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = None
if "interrupt_data" not in st.session_state:
    st.session_state.interrupt_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ----- ----- -----
# functions
# ----- ----- -----
def add_chat(role: str, content: str, msg_type: str = "text"):
	st.session_state.chat_history.append({
		"role": role,
		"content": content,
		"type": msg_type,
	})


def get_config():
	return {"configurable": {"thread_id": st.session_state.thread_id}}


def extract_interrupt_data():
	state = app.get_state(get_config())

	if not state.next:
		return None, None

	interrupt_data = None
	if state.tasks:
		for task in state.tasks:
			if hasattr(task, "interrupts") and task.interrupts:
				interrupt_data = task.interrupts[0].value

	return state.next, interrupt_data


def record_interrupt_response(data):
	if not isinstance(data, dict):
		return 

	if data.get("type") == "blog_review":
		proofread = data.get("proofread_text", "")
		self_review = data.get("self_review", {})
		score = self_review.get("score", "-")
		feedback = self_review.get("feedback", "")

		add_chat(
			"assistant",
			f"교정이 완료되었습니다. (자동 평가: {score}점)\n\n"
			f"{feedback}\n\n"
			f"---\n\n"
			f"{proofread}"
		)

	elif data.get("type") == "cards_review":
		cards = data.get("cards", [])

		# cards_text = "\n".join(
		#	f"**카드 {card.get('card_number')}** ({card.get('type', '')}): {card.get('title', '')}"
		#	for card in cards
		# )

		add_chat(
			"assistant", 
			cards,
			msg_type="cards"
		)


def run_pipeline(text: str):
	st.session_state.thread_id = f"post-{int(time.time())}"
	st.session_state.chat_history = []

	add_chat("human", text)

	try:	
		app.invoke(
			{
				"original_text": draft,
				"type": st.session_state.get("selected_type", "blog"),
				"platform": st.session_state.get("selected_platform", "blog"),
				"tone": st.session_state.get("selected_tone", "technical"),
				"title": text[:30],
				"row_id": st.session_state.thread_id,
				"chat_input": True,
			},
			get_config()
		)

		next_node, interrupt_data = extract_interrupt_data()

		if next_node:
			st.session_state.pipeline_status = "waiting"
			st.session_state.interrupt_data = interrupt_data
			record_interrupt_response(interrupt_data)
		else:
			st.session_state.pipeline_status = "done"
			add_chat("assistant", "파이프라인이 완료되었습니다.")

	except Exception as e:
		st.session_state.pipeline_status = "error"
		st.session_state.interrupt_data = str(e)
		add_chat(
			"assistant", 
			f"(Exception) 오류가 발생했습니다.\n\n{str(e)}"
		)


def resume_pipeline(response: str):
	try:
		app.invoke(Command(resume=response), get_config())
		next_node, interrupt_data = extract_interrupt_data()

		if next_node:
			st.session_state.pipeline_status = "waiting"
			st.session_state.interrupt_data = interrupt_data
			record_interrupt_response(interrupt_data)
		else:
			st.session_state.pipeline_status = "done"
			st.session_state.interrupt_data = None

			state = app.get_state(get_config())
			values = state.values

			output_paths = values.get("output_paths", [])
			if output_paths:
				add_chat("assistant", output_paths, msg_type="images")
			else:
				add_chat("assistant", "파이프라인이 완료되었습니다.")

	except Exception as e:
		st.session_state.pipeline_status = "error"
		st.session_state.interrupt_data = str(e)
		add_chat(
			"assistant", 
			f"(Exception) 오류가 발생했습니다.\n\n{str(e)}"
		)


# ----- ----- -----
# sidebar
# ----- ----- -----
with st.sidebar:
	st.title("Content pilot")
	st.caption("멀티채널 콘텐츠 파이프라인")
	
	st.divider()

	selected_type = st.selectbox(
    "원하는 타입을 선택하세요", 
    ["blog", "sns", "all"],
		key="selected_type",
  )
	if selected_type == "sns" or selected_type == "all":
		selected_platform = st.selectbox(
			"타겟 플랫폼을 선택하세요",
			["instagram", "linkedin", "threads"],
			key="selected_platform",
		)
	else:
		selected_platform = st.selectbox(
			"타겟 플랫폼을 선택하세요",
			["blog"],
			key="selected_platform",
		)
	selected_tone = st.selectbox(
		"글의 톤을 선택하세요", 
		["technical", "casual", "professional"], 
		key="selected_tone",
	)

	# check
	# print("type :", selected_type)
	# print("platform :", "" if selected_platform == "blog" else selected_platform)
	# print("tone :", selected_tone) 


	# st.caption("Google sheets에서 pending item을 찾아서 처리합니다.")
	# if st.button("파이프라인 실행 (1건)", use_container_width=True):
	#	run_pipeline()

	# if st.session_state.pipeline_status == "waiting":
	#	st.success("확인 대기 중")
	# elif st.session_state.pipeline_status == "done":
	#	st.success("처리 완료!")
	# elif st.session_state.pipeline_status == "empty":
	#	st.info("처리할 pending 항목이 없습니다.")
	# else:
	#	st.error(str(st.session_state.interrupt_data))

	st.divider()


# ----- ----- -----
# main

# ── 채팅 이력 표시 ──
for msg in st.session_state.chat_history:
	with st.chat_message(msg["role"]):

		# card news
		if msg.get("type") == "cards":
			st.markdown("**카드뉴스가 생성되었습니다.**")
			cards = msg["content"]

			cols = st.columns(min(len(cards), 3))
			for i, card in enumerate(cards):
				with cols[i % 3]:
					type_colors = {
						"hook": "🟣", "content": "🔵",
						"summary": "🟢", "cta": "🟠",
					}
					icon = type_colors.get(card.get("type", ""), "⚪")

					st.markdown(f"**{icon} 카드 {card.get('card_number', i+1)}** ({card.get('type', '')})")
					st.markdown(f"### {card.get('title', '')}")
					st.write(card.get("body", ""))
					st.caption(f"강조: {card.get('highlight', '')}")
		
		# images
		elif msg.get("type") == "images":
			st.markdown("**카드뉴스가 완성되었습니다.**")
			paths = msg["content"]

			cols = st.columns(min(len(paths), 3))
			for i, path in enumerate(paths):
				filepath = Path(path)
				if filepath.exists():
					with cols[i % 3]:
						st.image(str(filepath), caption=filepath.name)

		# text
		else:
			st.markdown(msg["content"])


if st.session_state.pipeline_status == "waiting" and st.session_state.interrupt_data:
	data = st.session_state.interrupt_data
	interrupt_type = data.get("type", "") if isinstance(data, dict) else ""
	print('check : ', interrupt_type)

	# ── 교정 결과 확인 ──
	if interrupt_type == "blog_review":
		auto_review = data.get("auto_review", {})
		if auto_review:
			col1, col2 = st.columns(2)
			with col1:
				st.metric("자동 평가 점수", f"{auto_review.get('review_score', 0)} / 10")
			with col2:
				st.info(auto_review.get("review_feedback", ""))

		if st.button("승인", type="primary"):
			add_chat("human", "승인")
			with st.spinner("진행 중..."):
				resume_pipeline("approve")
			st.rerun()

		st.caption("수정이 필요하면 하단 채팅창에 피드백을 입력하세요.")

	# ── 카드뉴스 확인 ──
	elif interrupt_type == "cards_review":
		cards = data.get("cards", [])
		if cards:
	#		cols = st.columns(min(len(cards), 3))
	#		for i, card in enumerate(cards):
	#			with cols[i % 3]:
	#				type_colors = {
	#					"hook": "🟣",
	#					"content": "🔵",
	#					"summary": "🟢",
	#					"cta": "🟠",
	#				}
	#				icon = type_colors.get(card.get("type", ""), "⚪")
	#
	#				st.markdown(f"**{icon} 카드 {card.get('card_number', i+1)}** ({card.get('type', '')})")
	#				st.markdown(f"### {card.get('title', '')}")
	#				st.write(card.get("body", ""))
	#				st.caption(f"강조: {card.get('highlight', '')}")
	#				st.divider()

			if st.button("승인", type="primary", key="cards_approve"):
				add_chat("human", "승인")
				with st.spinner("렌더링 중..."):
					resume_pipeline("approve")
				st.rerun()

			st.caption("수정이 필요하면 하단 채팅창에 피드백을 입력하세요.")


# ══════════════════════════════════════
#  완료 후: 결과 + 다운로드
# ══════════════════════════════════════
	elif st.session_state.pipeline_status == "done" and st.session_state.thread_id:
		state = app.get_state(get_config())
		values = state.values

		# 교정 결과
		proofread = values.get("proofread_text", "")
		if proofread:
			with st.expander("교정된 글 보기"):
				st.write(proofread)

    # JPG 미리보기 + 다운로드
		output_paths = values.get("output_paths", [])
		if output_paths:
			st.subheader("생성된 카드뉴스")

			cols = st.columns(min(len(output_paths), 3))
			for i, path in enumerate(output_paths):
				filepath = Path(path)
				print(f"[완료] {filepath} 존재 여부: {filepath.exists()}")
				print(f"[완료] 절대경로: {filepath.resolve()}")

				if filepath.exists():
					with cols[i % 3]:
						st.image(str(filepath), caption=filepath.name)

						with open(filepath, "rb") as f:
							st.download_button(
								label=f"다운로드",
								data=f.read(),
								file_name=filepath.name,
								mime="image/jpeg",
								use_container_width=True,
								key=f"download_{i}",
							)
				else:
					with cols[i % 3]:
						st.warning(f"파일을 찾을 수 없습니다 : {path}")
		else:
			st.warning(f"결과물을 찾을 수 없습니다 : {output_paths}")



# ----- ----- -----
# bottom
# ----- ----- -----
draft = st.chat_input("학습한 내용의 초안을 입력하세요.")
if draft:
	# interrupt 대기 중 → 피드백으로 처리
	if st.session_state.pipeline_status == "waiting":
		add_chat("human", draft)
		with st.spinner("피드백 반영 중..."):
			resume_pipeline(draft)
		st.rerun()
 
	# 대기 중이 아님 → 새 파이프라인 시작 (직접 입력)
	else:
		with st.spinner("파이프라인 실행 중..."):
			run_pipeline(draft)
		st.rerun()