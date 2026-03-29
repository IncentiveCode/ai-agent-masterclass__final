from main import app

# 그래프가 정상적으로 컴파일되었는지 확인
print("노드 목록:")
for node in app.get_graph().nodes:
	print(f"  - {node}")

print(f"\n총 노드 수: {len(app.get_graph().nodes)}")
print("그래프 컴파일 성공!")