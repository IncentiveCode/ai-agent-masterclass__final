from my_nodes.fetch_sheets import fetch_from_sheets

result = fetch_from_sheets({})
print(f"제목: {result['title']}")
print(f"타입: {result['type']}")
print(f"플랫폼: {result['platform']}")
print(f"톤: {result['tone']}")
print(f"본문 미리보기: {result['original_text'][:100]}...")