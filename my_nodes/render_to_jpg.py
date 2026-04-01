import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from state import State
from config import CARD_SIZES, DEFAULT_CARD_SIZE, OUTPUT_DIR, PLATFORM_STYLES, DEFAULT_STYLE

def load_template() -> str:
	template_path = Path(__file__).parent.parent / "templates" / "card_template.html"
	print(template_path)
	return template_path.read_text(encoding="utf-8")

def render_card_html(template: str, card: dict, platform: str, total: int) -> str:
	"""
	카드 데이터를 html 템플릿에 주입.
	"""

	size = CARD_SIZES.get(platform, DEFAULT_CARD_SIZE)
	style = PLATFORM_STYLES.get(platform, DEFAULT_STYLE)

	html = template
	replacements = {
		"{{width}}": str(size["width"]),
		"{{height}}": str(size["height"]),
		"{{bg_color}}": style["bg_color"],
		"{{accent_color}}": style["accent_color"],
		"{{title_size}}": str(style["title_size"]),
		"{{body_size}}": str(style["body_size"]),
		"{{card_number}}": str(card.get("card_number", 1)),
		"{{total_cards}}": str(total),
		"{{title}}": card.get("title", ""),
		"{{body}}": card.get("body", ""),
		"{{highlight}}": card.get("highlight", ""),
		"{{card_type}}": card.get("type", "content"),
  }

	for key, value in replacements.items():
		html = html.replace(key, value)
		
	return html

def render_to_jpg(state: State):
	"""
	카드 데이터 JSON을 JPG 이미지로 렌더링.
	"""

	cards = state.get("cards", [])
	platform = state.get("platform", "instagram")
	row_id = state.get("row_id", "unknown")
	size = CARD_SIZES.get(platform, DEFAULT_CARD_SIZE)

	output_dir = Path(OUTPUT_DIR) / row_id
	output_dir.mkdir(parents=True, exist_ok=True)
	template = load_template()
	output_paths = []

	with sync_playwright() as p:
		browser = p.chromium.launch()
		page = browser.new_page(
			viewport={
				"width": size["width"],
				"height": size["height"],
			}
		)

		for card in cards:
			html = render_card_html(template, card, platform, len(cards))
			page.set_content(html, wait_until="networkidle")
			filename = f"card_{card.get('card_number', 0):02d}.jpg"
			filepath = str(output_dir / filename)

			page.screenshot(
				path=filepath,
				type="jpeg",
				quality=90,
			)

			output_paths.append(filepath)
			print(f"[render] 카드 {card.get('card_number')} 저장 : {filepath}")
		
		browser.close()
		p.stop()
	
	return {"output_paths": output_paths}
