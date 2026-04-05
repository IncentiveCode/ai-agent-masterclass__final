import json
from state import State
from config import get_sheets_client


def save_to_sheets(state: State):
	"""
	처리 결과를 google sheets 에 저장한다.
	"""

	if state.get("chat_input") == True:
		print(f"[save_to_sheets] sheet 저장 없이 완료 (status: done)")
		return {}

	sheet = get_sheets_client()

	row_id = state.get("row_id", "")
	if not row_id:
		print("[save_to_sheets] row_id 가 없습니다. 저장 없이 종료합니다.")
		return {}

	try:
		cell = sheet.find(row_id)
		row_index = cell.row
	except Exception as e:
		print(f"[save_to_sheets] row_id '{row_id}' 를 찾을 수 없습니다: {e}")
		return {}

	headers = sheet.row_values(1)
	def col_index(name: str) -> int:
		"""
		헤더 이름으로 컬럼 번호를 찾는다.
		"""

		try:
			return headers.index(name) + 1
		except ValueError:
			return -1

	updates = {
		"proofread": state.get("proofread_text", ""),
		"cards_json": json.dumps(
			state.get("cards", []),
			ensure_ascii=False,
		),
		"output_paths": ", ".join(state.get("output_paths", [])),
		"status": "done",
	}

	for col_name, value in updates.items():
		col = col_index(col_name)
		if col > 0:
			sheet.update_cell(row_index, col, value)
		else:
			print(f"[save_to_sheets] '{col_name}' 컬럼을 찾을 수 없습니다.")

	print(f"[save_to_sheets] row {row_index} 저장 완료 (status: done)")
	return {}


def on_error(state: State):
	"""
	파이프라인 실패시 status를 error로 업데이트.
	"""

	sheet = get_sheets_client()
	row_id = state.get("row_id", "")

	if not row_id:
		return {}

	try:
		cell = sheet.find(row_id)
		headers = sheet.row_values(1)
		status_col = headers.index("status") + 1
		sheet.update_cell(cell.row, status_col, "error")
		print(f"[on_error] row {cell.row} status → error")
	except Exception as e:
		print(f"[on_error] 에러 상태 저장 실패: {e}")

	return {}