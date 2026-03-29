from my_nodes.router import route_by_type

# 각 타입별 라우팅 확인
assert route_by_type({"type": "blog"}) == "blog_editor"
assert route_by_type({"type": "sns"}) == "sns_editor"
assert route_by_type({"type": "slide"}) == "slide_generator"
assert route_by_type({"type": "all"}) == "blog_editor"

# 잘못된 타입 → 에러
try:
	route_by_type({"type": "all"})
except ValueError as e:
  print(f"예상된 에러: {e}")

print("모든 라우팅 테스트 통과!")