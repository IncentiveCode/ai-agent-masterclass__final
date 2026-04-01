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


# ----- ----- -----
# functions
# ----- ----- -----
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


def run_pipeline():
	st.session_state.thread_id = f"post-{int(time.time())}"

	try:
		app.invoke({"original_text": ""}, get_config())

		next_node, interrupt_data = extract_interrupt_data()

		if next_node:
			st.session_state.pipeline_status = "waiting"
			st.session_state.interrupt_data = interrupt_data
		else:
			st.session_state.pipeline_status = "done"

	except ValueError as e:
		st.session_state.pipeline_status = "empty"
		st.session_state.interrupt_data = str(e)
	except Exception as e:
		st.session_state.pipeline_status = "error"
		st.session_state.interrupt_data = str(e)


def resume_pipeline(response: str):
	try:
		app.invoke(Command(resume=response), get_config())

		next_node, interrupt_data = extract_interrupt_data()

		if next_node:
			st.session_state.pipeline_status = "waiting"
			st.session_state.interrupt_data = interrupt_data
		else:
			st.session_state.pipeline_status = "done"
			st.session_state.interrupt_data = None

	except Exception as e:
		st.session_state.pipeline_status = "error"
		st.session_state.interrupt_data = str(e)


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
	selected_tone = st.selectbox(
		"글의 톤을 선택하세요", 
		["technical", "casual", "professional"], 
		key="selected_tone",
	)


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
# ----- ----- -----
st.header("콘텐츠 확인")
if st.session_state.pipeline_status == "waiting" and st.session_state.interrupt_data:
	data = st.session_state.interrupt_data
	interrupt_type = data.get("type", "") if isinstance(data, dict) else ""
	print('check : ', interrupt_type)

	# ── 교정 결과 확인 ──
	if interrupt_type == "blog_review":
		st.subheader("교정 결과 확인")

		auto_review = data.get("auto_review", {})
		if auto_review:
			col1, col2 = st.columns(2)
			with col1:
				st.metric("자동 평가 점수", f"{auto_review.get('score', 0)} / 10")
			with col2:
				st.info(auto_review.get("feedback", ""))

			st.text_area(
				"교정된 글",
				value=data.get("proofread_text", ""),
				height=300,
				disabled=True,
			)

			col1, col2 = st.columns([1, 3])
			with col1:
				if st.button("승인", type="primary", use_container_width=True):
					with st.spinner("진행 중..."):
						resume_pipeline("approve")
						st.rerun()

			with col2:
				feedback = st.text_input(
					"수정 피드백",
					placeholder="두 번째 문단을 좀 더 부드럽게 해주세요",
				)
				if st.button("피드백 보내기") and feedback:
					with st.spinner("재교정 중..."):
						resume_pipeline(feedback)
						st.rerun()

	# ── 카드뉴스 확인 ──
	elif interrupt_type == "cards_review":
		st.subheader("카드뉴스 확인")

		cards = data.get("cards", [])
		if cards:
			cols = st.columns(min(len(cards), 3))
			for i, card in enumerate(cards):
				with cols[i % 3]:
					type_colors = {
						"hook": "🟣",
						"content": "🔵",
						"summary": "🟢",
						"cta": "🟠",
					}
					icon = type_colors.get(card.get("type", ""), "⚪")

					st.markdown(f"**{icon} 카드 {card.get('card_number', i+1)}** ({card.get('type', '')})")
					st.markdown(f"### {card.get('title', '')}")
					st.write(card.get("body", ""))
					st.caption(f"강조: {card.get('highlight', '')}")
					st.divider()

			col1, col2 = st.columns([1, 3])
			with col1:
				if st.button("승인", type="primary", use_container_width=True, key="cards_approve"):
					with st.spinner("렌더링 중..."):
						resume_pipeline("approve")
					st.rerun()

			with col2:
				feedback = st.text_input(
					"수정 피드백",
					placeholder="카드 2번 내용을 좀 더 간결하게",
					key="cards_feedback",
				)
				if st.button("피드백 보내기", key="cards_fb_btn") and feedback:
					with st.spinner("카드 재생성 중..."):
						resume_pipeline(feedback)
					st.rerun()


# ══════════════════════════════════════
#  완료 후: 결과 + 다운로드
# ══════════════════════════════════════
	elif st.session_state.pipeline_status == "done" and st.session_state.thread_id:
		st.subheader("처리 완료")
		
		state = app.get_state(get_config())
		values = state.values

		st.success(f"Thread: {st.session_state.thread_id}")
		st.write(f"콘텐츠 타입: **{values.get('content_type', '-')}**")

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



# ----- ----- -----
# bottom
# ----- ----- -----
draft = st.chat_input("학습한 내용을 입력하세요.")
if draft:
	selected_type = st.session_state.selected_type
	selected_platform = "blog" if selected_type != "blog" else st.session_state.selected_platform
	selected_tone = st.session_state.selected_tone

	with st.chat_message("human"):
		st.write(f"타겟 플랫폼 : {selected_type}")
		st.write(f"초안 : {draft}")

	st.session_state.thread_id = f"ui-{int(time.time())}"
	config = get_config()
	app.invoke({
    "original_text": draft,
    "type": selected_type,
    "platform": selected_platform,
    "tone": selected_tone,
    "title": "UI 입력",
    "row_id": st.session_state.thread_id,
	}, config)

	next_node, interrupt_data = extract_interrupt_data()
	if next_node:
		st.session_state.pipeline_status = "waiting"
		st.session_state.interrupt_data = interrupt_data
	else:
		st.session_state.pipeline_status = "done"

	st.rerun()