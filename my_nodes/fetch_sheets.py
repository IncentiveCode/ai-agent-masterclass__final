from config import get_sheets_client
from state import State

def fetch_from_sheets(state: State):
	sheet = get_sheets_client()
	records = sheet.get_all_records()

	target = None
	target_row_index = None

	for i, record in enumerate(records):
		if record.get("status", "").strip().lower() == "pending":
			target = record
			target_row_index = i + 2
			break

	if target is None:
		raise ValueError("처리할 pending 항목이 없습니다.")

	status_col = sheet.find("status").col
	sheet.update_cell(target_row_index, status_col, "processing")

	return {
		"row_id": str(target.get("row_id", "")),
		"title": str(target.get("title", "")),
		"original_text": str(target.get("original_text", "")),
		"type": str(target.get("type", "")),
		"platform": str(target.get("platform", "")),
		"tone": str(target.get("tone", "")),
	}