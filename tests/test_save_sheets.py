from my_nodes.save_to_sheets import save_to_sheets

test_state = {
	"row_id": "1",  # 시트에 실제로 있는 row_id
	"proofread_text": "테스트 교정 결과입니다.",
	"cards": [
		{"card_number": 1, "title": "테스트", "body": "본문", "highlight": "강조", "type": "hook"}
	],
	"output_paths": ["output/001/card_01.jpg"],
}

save_to_sheets(test_state)
print("시트를 확인해보세요!")