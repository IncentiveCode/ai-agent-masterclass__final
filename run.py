from langgraph.types import Command
from main import app


def run_pipeline():
	config = {"configurable": {"thread_id": "post-001"}}

	print("=" * 60)
	print(" Content-Pilot 실행 ")
	print("=" * 60)

	# ── 1) 첫 실행: 시트에서 읽기 → 에디터 → self_review → interrupt에서 멈춤 ──
	print("\n[1] 파이프라인 시작...")
	result = app.invoke({"original_text": ""}, config)
	# original_text는 빈 값 — fetch_from_sheets에서 시트 데이터로 채워짐

	# interrupt에서 멈추면 현재 상태를 확인할 수 있음
	state = app.get_state(config)
	print(f"\n현재 노드: {state.next}")

	# interrupt가 보내온 데이터 확인
	if state.tasks:
		for task in state.tasks:
			if hasattr(task, "interrupts") and task.interrupts:
				interrupt_data = task.interrupts[0].value
				print(f"확인 요청: {interrupt_data.get('message', '')}")

				# 교정된 글 미리보기
				if "proofread_text" in interrupt_data:
					text = interrupt_data["proofread_text"]
					print(f"\n--- 교정 결과 미리보기 ---")
					print(f"{text[:300]}...")

				# 카드뉴스 미리보기
				elif "cards" in interrupt_data:
					for card in interrupt_data["cards"]:
						print(f"\n  카드 {card['card_number']}: {card['title']}")
			
			
	# ── 2) 사용자 입력 받기 ──
	print("\n" + "-" * 40)
	user_input = input("승인(approve) 또는 피드백 입력: ").strip()
	if not user_input:
		user_input = "approve"


	# ── 3) resume으로 그래프 재개 ──
	print(f"\n[2] '{user_input}' 으로 재개...")
	result = app.invoke(Command(resume=user_input), config)

	# 다시 interrupt에서 멈출 수 있음 (sns 경로의 review_cards)
	state = app.get_state(config)
	if state.next:
		print(f"\n현재 노드: {state.next}")

		if state.tasks:
			for task in state.tasks:
				if hasattr(task, "interrupts") and task.interrupts:
					interrupt_data = task.interrupts[0].value
					print(f"확인 요청: {interrupt_data.get('message', '')}")

					if "cards" in interrupt_data:
						for card in interrupt_data["cards"]:
							print(f"  카드 {card['card_number']}: {card['title']}")

		print("\n" + "-" * 40)
		user_input = input("승인(approve) 또는 피드백 입력: ").strip()
		if not user_input:
			user_input = "approve"

		print(f"\n[3] '{user_input}' 으로 재개...")
		result = app.invoke(Command(resume=user_input), config)

	# ── 4) 완료 확인 ──
	final_state = app.get_state(config)

	if not final_state.next:
		print("\n" + "=" * 60)
		print(" 파이프라인 완료!")
		print("=" * 60)
		print(f"교정된 글: {final_state.values.get('proofread_text', '')[:200]}...")

		output_paths = final_state.values.get("output_paths", [])
		if output_paths:
			print(f"\n생성된 파일:")
			for path in output_paths:
				print(f"  → {path}")
	else:
		print(f"\n아직 진행 중: {final_state.next}")


def get_graph():
	app.get_graph().draw_mermaid_png(output_file_path="./output/graph.png")


if __name__ == "__main__":
  run_pipeline()
	# get_graph()