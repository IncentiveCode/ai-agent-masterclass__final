from main import app

config = {"configurable": {"thread_id": "post-001"}}

# 저장된 모든 상태 기록 가져오기
history = list(app.get_state_history(config))

print(f"총 {len(history)}개의 체크포인트\n")

for i, snapshot in enumerate(history):
	node = snapshot.next
	score = snapshot.values.get("review_score", "-")
	content_type = snapshot.values.get("content_type", "-")
	print(f"[{i}] 다음 노드: {node} | 점수: {score} | 타입: {content_type}")

# 특정 시점으로 돌아가기
if len(history) >= 3:
	past = history[2]  # 3번째 체크포인트로 돌아가기
	print(f"\n--- 체크포인트 [{2}]로 돌아가기 ---")
	print(f"다음 노드: {past.next}")
	print(f"교정 텍스트: {past.values.get('proofread_text', '')[:100]}...")

	# 이 시점부터 다시 실행할 수 있음
	# result = app.invoke(None, past.config)