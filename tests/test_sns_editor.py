from my_nodes.sns_editor import sns_editor

test_state = {
	"original_text": """개인사업자와 프리랜서를 위한 보험 점검 서비스를 준비하고 있습니다.
AI가 현재 보험 가입 현황을 분석하고 부족한 부분을 찾아드립니다.
랜딩페이지에서 간단한 정보를 입력하시면 무료 점검 리포트를 받아보실 수 있습니다.""",
	"platform": "instagram",
	"tone": "casual",
	"feedback": "",
}

result = sns_editor(test_state)
print("=== SNS 교정 결과 (instagram / casual) ===")
print(result["proofread_text"])