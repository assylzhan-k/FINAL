import html
import logging
import aiohttp

logger = logging.getLogger(__name__)
OPENTDB_URL = "https://opentdb.com/api.php"
ONLINE_CATEGORIES = [
    ("🔬 Science & Nature",   17),
    ("💻 Computers",          18),
    ("🎬 Film",               11),
    ("🎵 Music",              12),
    ("⚽ Sports",             21),
    ("🌍 Geography",          22),
    ("📜 History",            23),
    ("🎨 Art",                25),
    ("🐾 Animals",            27),
    ("🚗 Vehicles",           28),
]
_CODE_SUCCESS      = 0
_CODE_NO_RESULTS   = 1
_CODE_INVALID      = 2
_CODE_TOKEN_EMPTY  = 3
_CODE_TOKEN_NOT_FOUND = 4

def get_online_category_names() -> list[str]:
    return [name for name, _ in ONLINE_CATEGORIES]
def _category_id(display_name: str) -> int | None:
    for name, cid in ONLINE_CATEGORIES:
        if name == display_name:
            return cid
    return None
async def fetch_questions(category_name: str, amount: int = 5) -> list[dict] | None:
    import random
    category_id = _category_id(category_name)
    if category_id is None:
        logger.error("Unknown online category: %s", category_name)
        return None
    params = {
        "amount":     amount,
        "category":   category_id,
        "type":       "multiple",
        "difficulty": "medium",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(OPENTDB_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.error("OpenTDB HTTP error: %s", resp.status)
                    return None
                data = await resp.json()
    except aiohttp.ClientError as e:
        logger.error("OpenTDB connection error: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error fetching trivia: %s", e)
        return None
    if data.get("response_code") != _CODE_SUCCESS:
        logger.warning("OpenTDB response code: %s", data.get("response_code"))
        return None
    results = data.get("results", [])
    if not results:
        return None
    questions = []
    for item in results:
        question_text    = html.unescape(item["question"])
        correct          = html.unescape(item["correct_answer"])
        incorrect        = [html.unescape(a) for a in item["incorrect_answers"]]
        options = incorrect + [correct]
        random.shuffle(options)
        questions.append({
            "question":    question_text,
            "options":     options,
            "answer":      correct,
            "explanation": f"The correct answer is: {correct}",
        })
    return questions