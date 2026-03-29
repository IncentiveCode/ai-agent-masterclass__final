from my_nodes.card_generator import card_generator

test_state = {
    "proofread_text": """개인사업자와 프리랜서를 위한 보험 점검 서비스를 준비하고 있습니다.
AI가 현재 보험 가입 현황을 분석하고 부족한 부분을 찾아드립니다.
랜딩페이지에서 간단한 정보를 입력하시면 무료 점검 리포트를 받아보실 수 있습니다.""",
    "platform": "linkedin",
    "tone": "casual",
    "feedback": "",
}

result = card_generator(test_state)

print(f"카드 수: {len(result['cards'])}")
for card in result["cards"]:
    print(f"\n--- 카드 {card['card_number']} ({card['type']}) ---")
    print(f"제목: {card['title']}")
    print(f"본문: {card['body']}")
    print(f"강조: {card['highlight']}")