import os
import dotenv
dotenv.load_dotenv()

import gspread
from google.oauth2.service_account import Credentials

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
GOOGLE_SA_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# platform 별 카드 크기
CARD_SIZES = {
	"instagram": { "width": 1080, "height": 1080 },
	"linkedin": { "width": 1200, "height": 628 },
	"threads": { "width": 1080, "height": 1360 },
}
DEFAULT_CARD_SIZE = CARD_SIZES["instagram"]
OUTPUT_DIR = "output"

# platform 별 스타일 설정
PLATFORM_STYLES = {
	"instagram": {
		"bg_color": "#FAFAFA",
		"accent_color": "#6C5CE7",
		"title_size": 42,
		"body_size": 24,
	},
	"linkedin": {
		"bg_color": "#F5F5F0",
		"accent_color": "#0A66C2",
		"title_size": 36,
		"body_size": 22,
  },
  "threads": {
		"bg_color": "#FFFFFF",
		"accent_color": "#000000",
		"title_size": 44,
		"body_size": 26,
  },
}
DEFAULT_STYLE = PLATFORM_STYLES["instagram"]

def get_sheets_client():
	credentials = Credentials.from_service_account_file(
		GOOGLE_SA_JSON, scopes=SCOPES
	)
	client = gspread.authorize(credentials)
	return client.open_by_key(GOOGLE_SHEETS_ID).sheet1