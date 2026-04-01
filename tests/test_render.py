from my_nodes.render_to_jpg import render_to_jpg

test_state = {
	"row_id": "test-001",
	"platform": "instagram",
	"cards": [
		{
			"card_number": 1,
			"title": "보험, 진짜 제대로\n들고 있어요?",
			"body": "프리랜서, 1인 사업자라면\n보험 점검 한 번쯤 해봐야 해요",
			"highlight": "무료 AI 점검 리포트",
			"type": "hook",
		},
		{
			"card_number": 2,
			"title": "이런 분들 주목",
			"body": "개인사업자, 프리랜서\n소규모 자영업자",
			"highlight": "나도 해당될까?",
			"type": "content",
		},
		{
			"card_number": 3,
			"title": "지금 바로 점검해보세요",
			"body": "프로필 링크에서 무료 점검 시작",
			"highlight": "무료 · 3분 · AI 기반",
			"type": "cta",
		},
	],
}

result = render_to_jpg(test_state)
print(f"\n생성된 파일 {len(result['output_paths'])}개:")
for path in result["output_paths"]:
	print(f"  → {path}")