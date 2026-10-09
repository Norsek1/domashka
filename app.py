import base64
import io
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
from pydantic import BaseModel

ASSETS = Path(__file__).parent
HISTORY_FILE = ASSETS / "history.jsonl"


C = {
    "bg": "#f7f5ee", "card": "#fffefa", "border": "#e0e2d6",
    "primary": "#3d6347", "text": "#29372d", "muted": "#74796e",
    "mint": "#e9efe3", "warn_bg": "#f7eee4", "warn": "#8b593b",
    "off_bg": "#e3e6dc", "off_text": "#8d9386", "dash": "#bcc8b3",
}


ICONS = {
    "chef-hat": '<path d="M17 21a1 1 0 0 0 1-1v-5.35c0-.457.316-.844.727-1.041a4 4 0 0 0-2.134-7.589 5 5 0 0 0-9.186 0 4 4 0 0 0-2.134 7.588c.411.198.727.585.727 1.041V20a1 1 0 0 0 1 1Z" /> <path d="M6 17h12" />',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2" /> <circle cx="9" cy="9" r="2" /> <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />',
    "circle-alert": '<circle cx="12" cy="12" r="10" /> <line x1="12" x2="12" y1="8" y2="12" /> <line x1="12" x2="12.01" y1="16" y2="16" />',
    "scan-line": '<path d="M3 7V5a2 2 0 0 1 2-2h2" /> <path d="M17 3h2a2 2 0 0 1 2 2v2" /> <path d="M21 17v2a2 2 0 0 1-2 2h-2" /> <path d="M7 21H5a2 2 0 0 1-2-2v-2" /> <path d="M7 12h10" />',
    "upload": '<path d="M12 3v12" /> <path d="m17 8-5-5-5 5" /> <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />',
    "check": '<path d="M20 6 9 17l-5-5" />',
    "sparkles": '<path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z" /> <path d="M20 2v4" /> <path d="M22 4h-4" /> <circle cx="4" cy="20" r="2" />',
    "info": '<circle cx="12" cy="12" r="10" /> <path d="M12 16v-4" /> <path d="M12 8h.01" />',
    "circle-check": '<circle cx="12" cy="12" r="10" /> <path d="m16 9-5.5 5.5L8 12" />',
    "image-up": '<path d="M10.3 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10l-3.1-3.1a2 2 0 0 0-2.814.014L6 21" /> <path d="m14 19.5 3-3 3 3" /> <path d="M17 22v-5.5" /> <circle cx="9" cy="9" r="2" />',
    "sun": '<circle cx="12" cy="12" r="4" /> <path d="M12 2v2" /> <path d="M12 20v2" /> <path d="m4.93 4.93 1.41 1.41" /> <path d="m17.66 17.66 1.41 1.41" /> <path d="M2 12h2" /> <path d="M20 12h2" /> <path d="m6.34 17.66-1.41 1.41" /> <path d="m19.07 4.93-1.41 1.41" />',
    "focus": '<circle cx="12" cy="12" r="3" /> <path d="M3 7V5a2 2 0 0 1 2-2h2" /> <path d="M17 3h2a2 2 0 0 1 2 2v2" /> <path d="M21 17v2a2 2 0 0 1-2 2h-2" /> <path d="M7 21H5a2 2 0 0 1-2-2v-2" />',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /> <path d="M3 3v5h5" /> <path d="M12 7v5l4 2" />',
    "trash": '<path d="M3 6h18" /> <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" /> <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /> <line x1="10" x2="10" y1="11" y2="17" /> <line x1="14" x2="14" y1="11" y2="17" />'
}


def icon(name: str, size: int = 18, color: str = C["primary"], sw: float = 1.9) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="flex:none">{ICONS[name]}</svg>'
    )


def icon_uri(name: str, size: int = 30, color: str = C["primary"]) -> str:
    svg = icon(name, size, color).replace("#", "%23").replace('"', "'")
    return f'url("data:image/svg+xml;utf8,{svg}")'


DEMO_RECIPE = {
    "name": "Спагеті з томатами та базиліком",
    "ingredients": [
        ("Спагеті", "200 г"), ("Оливкова олія", "2 ст. л."),
        ("Помідори", "400 г"), ("Свіжий базилік", "6–8 листків"),
        ("Часник", "2 зубчики"), ("Сіль і чорний перець", "за смаком"),
    ],
    "steps": [
        ("Підготуйте продукти", "Помийте помідори й базилік. Наріжте помідори невеликими кубиками, а часник — тонкими скибочками."),
        ("Зваріть спагеті", "Закип’ятіть 2 л води, додайте 1 ч. л. солі. Варіть спагеті за інструкцією на пакуванні. Перед зливанням збережіть ½ склянки води."),
        ("Приготуйте соус", "На середньому вогні розігрійте олію. Обсмажте часник 30 секунд, не підрум’янюючи. Додайте помідори й тушкуйте 10–12 хвилин, помішуючи."),
        ("З’єднайте все разом", "Перекладіть спагеті в соус. Додайте 2–3 ст. л. збереженої води й перемішайте. Якщо соус густий, додайте ще трохи води."),
        ("Приправте й подавайте", "Додайте сіль і перець за смаком. Порвіть листки базиліку, посипте ними пасту та подавайте теплою."),
    ],
}


MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash"]

PROMPT = """Ти — кулінарний помічник. Подивись на фото.
Якщо на фото є приготована страва — визнач її й склади приблизний покроковий рецепт для 2 порцій.
Якщо на фото НЕ їжа або страву неможливо визначити — постав is_dish = false, решту полів залиш порожніми.
Відповідай українською. Кількості пиши коротко («200 г», «2 ст. л.», «за смаком»).
Роби 4-7 кроків, кожен — короткий заголовок і 1-2 речення."""


class IngredientOut(BaseModel):
    name: str
    quantity: str


class StepOut(BaseModel):
    title: str
    text: str


class RecipeOut(BaseModel):
    is_dish: bool
    name: str
    ingredients: list[IngredientOut]
    steps: list[StepOut]


def _secret(key: str, default: str | None = None) -> str | None:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    try:
        import tomllib
        f = Path(__file__).parent / ".streamlit" / "secrets.toml"
        if f.exists():
            val = tomllib.loads(f.read_text(encoding="utf-8")).get(key)
            if val:
                return val
    except Exception:
        pass
    return os.environ.get(key, default)


def mime_of(name: str) -> str:
    return "image/png" if name.lower().endswith("png") else "image/jpeg"


def _thumb_b64(image_bytes: bytes, mime: str) -> str | None:
    if not image_bytes:
        return None
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((96, 96))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=55)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def log_history(status: str, image_bytes: bytes, mime: str,
                 dish: str | None = None, model: str | None = None, note: str | None = None) -> None:
    entry = {
        "id": uuid.uuid4().hex[:8],
        "ts": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "status": status,
        "dish": dish,
        "model": model,
        "note": note,
        "thumb": _thumb_b64(image_bytes, mime),
    }
    try:
        with HISTORY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def load_history(limit: int = 200) -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    out = []
    try:
        for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        return []
    out.reverse()
    return out[:limit]


def demo_fallback(note: str, image_bytes: bytes = b"", mime: str = "image/jpeg") -> dict:
    st.session_state.demo_note = note
    log_history("demo", image_bytes, mime, note=note)
    return DEMO_RECIPE


def generate_recipe(image_bytes: bytes, mime: str) -> dict | None:
    st.session_state.demo_note = None
    st.session_state.source = None
    key = _secret("GEMINI_API_KEY")
    if not key:
        return demo_fallback(
            "Демо-режим: ключ GEMINI_API_KEY не знайдено. Створіть файл .streamlit/secrets.toml (саме secrets.toml, не .example) і перезапустіть застосунок.",
            image_bytes, mime)
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    contents = [types.Part.from_bytes(data=image_bytes, mime_type=mime), PROMPT]
    config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=RecipeOut)


    models = [_secret("GEMINI_MODEL", MODEL)] + [m for m in FALLBACK_MODELS if m != _secret("GEMINI_MODEL", MODEL)]
    out, last_err = None, None
    for model in models:
        for attempt in range(4):
            try:
                resp = client.models.generate_content(model=model, contents=contents, config=config)
                out = resp.parsed or RecipeOut.model_validate_json(resp.text)
                st.session_state.source = model
                break
            except Exception as e:
                last_err = e
                code = getattr(e, "code", None) or getattr(e, "status_code", None)
                err_str = str(e)
                if code in (429, 500, 503, 504) or "503" in err_str or "UNAVAILABLE" in err_str or "overloaded" in err_str.lower():
                    if attempt < 3:
                        time.sleep(3 * (attempt + 1))
                        continue
                break
        if out is not None:
            break
    if out is None:
        return demo_fallback(
            f"Демо-режим: помилка Gemini — {type(last_err).__name__}: {str(last_err)[:160]}",
            image_bytes, mime)

    if not out.is_dish or not out.ingredients or not out.steps:
        log_history("no_dish", image_bytes, mime, model=st.session_state.get("source"))
        return None
    log_history("success", image_bytes, mime, dish=out.name, model=st.session_state.get("source"))
    return {
        "name": out.name,
        "ingredients": [(i.name, i.quantity) for i in out.ingredients],
        "steps": [(x.title, x.text) for x in out.steps],
    }


def base_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Lora:wght@400;500&display=swap');
.stApp, .stApp p, .stApp label, .stApp button {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {C['bg']}; color: {C['text']}; }}
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"] {{ display: none !important; }}
.block-container {{ padding: 0 !important; max-width: 1200px !important; }}
[data-testid="stVerticalBlock"] {{ gap: 0; }}
h1,h2,h3,.serif {{ font-family: 'Lora', serif !important; font-weight: 400 !important; }}

.fs-header {{ height: 88px; padding: 0 64px; display: flex; align-items: center;
  justify-content: space-between; border-bottom: 1px solid {C['border']}; }}
.fs-brand {{ display: flex; align-items: center; gap: 12px; }}
.fs-mark {{ width: 38px; height: 38px; border-radius: 12px; background: {C['primary']};
  display: flex; align-items: center; justify-content: center; }}
.fs-name {{ font-size: 21px; color: {C['text']}; }}
.fs-desc {{ font-size: 13px; color: {C['muted']}; }}
.fs-footer {{ padding: 24px 64px; display: flex; justify-content: space-between;
  border-top: 1px solid {C['border']}; font-size: 12px; color: {C['muted']}; margin-top: 32px; }}

.fs-intro {{ display: flex; flex-direction: column; gap: 20px; margin-bottom: 32px; }}
.fs-flow {{ display: flex; align-items: center; gap: 14px; }}
.fs-step {{ display: flex; align-items: center; gap: 8px; font-size: 12px; color: {C['muted']}; }}
.fs-step.on {{ color: {C['primary']}; font-weight: 600; }}
.fs-dot {{ width: 23px; height: 23px; border-radius: 99px; background: {C['off_bg']}; color: {C['muted']};
  font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; }}
.fs-step.on .fs-dot {{ background: {C['primary']}; color: #fff; }}
.fs-line {{ width: 30px; height: 1px; background: {C['border']}; }}
.fs-title {{ font-family: 'Lora', serif; font-size: 38px; line-height: 46px; margin: 0 0 10px; color: {C['text']}; }}
.fs-sub {{ font-size: 16px; color: {C['muted']}; line-height: 24px; margin: 0; }}

.st-key-workspace {{ padding: 40px 64px 0; }}

.st-key-upload_card, .st-key-photo_card, .st-key-error_photo, .st-key-error_card {{
  background: {C['card']}; border: 1px solid {C['border']}; border-radius: 18px; overflow: hidden; }}
.st-key-upload_card {{ padding: 24px; gap: 16px; }}
.st-key-error_card {{ padding: 32px; gap: 24px; }}
.fs-sec-head {{ display: flex; justify-content: space-between; align-items: center; }}
.fs-sec-head b {{ font-size: 16px; font-weight: 600; }}
.fs-sec-head span {{ font-size: 12px; color: {C['muted']}; }}

.st-key-upload_card [data-testid="stFileUploaderDropzone"] > div:first-child {{ order: 1; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] > button {{ order: 2; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] {{
  background: {C['bg']}; border: 1px dashed {C['dash']}; border-radius: 10px; min-height: 258px;
  flex-direction: column; justify-content: center; align-items: center; gap: 14px; padding: 24px; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"]::before {{
  content: ""; width: 62px; height: 62px; border-radius: 20px; background-color: {C['mint']};
  background-image: {icon_uri('image-up')}; background-repeat: no-repeat; background-position: center; }}
.st-key-upload_card [data-testid="stFileUploaderDropzoneInstructions"] > div {{ display: none; }}
.st-key-upload_card [data-testid="stFileUploaderDropzoneInstructions"] {{ text-align: center; display: flex; flex-direction: column; align-items: center; }}
.st-key-upload_card [data-testid="stFileUploaderDropzoneInstructions"]::before {{
  content: "Перетягніть фото сюди"; display: block; font-size: 16px; font-weight: 500; color: {C['text']}; margin-bottom: 6px; }}
.st-key-upload_card [data-testid="stFileUploaderDropzoneInstructions"]::after {{
  content: "або виберіть його на комп’ютері"; display: block; font-size: 13px; color: {C['muted']}; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] button {{
  background: {C['card']}; border: 1px solid {C['border']}; border-radius: 8px; height: 36px; padding: 0 18px;
  font-size: 0; display: inline-flex; align-items: center; gap: 8px; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] button > * {{ display: none !important; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] button::before {{
  content: ""; width: 16px; height: 16px; background: {icon_uri('upload', 16, C['primary'])} no-repeat center; }}
.st-key-upload_card [data-testid="stFileUploaderDropzone"] button::after {{
  content: "Вибрати фото"; font-size: 13px; font-weight: 600; color: {C['primary']}; }}

.st-key-generate button, .st-key-retry button, .st-key-retry_small button {{
  height: 48px; border-radius: 10px; width: 100%; font-weight: 600; font-size: 14px; border: 0; }}
.st-key-generate button, .st-key-retry button {{ background: {C['primary']}; color: #fff; }}
.st-key-generate button p, .st-key-retry button p {{ color: #fff; font-size: 14px; font-weight: 600; }}
.st-key-generate button, .st-key-retry button, .st-key-retry_small button {{ display: inline-flex; align-items: center; justify-content: center; gap: 10px; }}
.st-key-generate button::before {{ content: ""; width: 18px; height: 18px; background: {icon_uri('sparkles', 18, '#ffffff')} no-repeat center; }}
.st-key-generate button:disabled::before {{ background: {icon_uri('sparkles', 18, C['off_text'])} no-repeat center; }}
.st-key-retry button::before {{ content: ""; width: 18px; height: 18px; background: {icon_uri('upload', 18, '#ffffff')} no-repeat center; }}
.st-key-retry_small button::before {{ content: ""; width: 18px; height: 18px; background: {icon_uri('upload', 18, C['primary'])} no-repeat center; }}
.st-key-back button {{ background: transparent; border: 0; padding: 0 0 20px; min-height: 0; width: auto; }}
.st-key-back button p {{ color: {C['muted']}; font-size: 14px; font-weight: 500; }}
.st-key-back button:hover p {{ color: {C['primary']}; }}
.fs-thumb {{ display: flex; gap: 14px; align-items: center; background: {C['bg']}; border: 1px solid {C['border']};
  border-radius: 10px; padding: 10px; }}
.fs-thumb img {{ width: 72px; height: 72px; object-fit: cover; border-radius: 8px; }}
.fs-thumb b {{ display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; }}
.fs-thumb span {{ font-size: 11px; color: {C['muted']}; }}
.st-key-generate button:disabled {{ background: {C['off_bg']}; }}
.st-key-generate button:disabled p {{ color: {C['off_text']}; }}
.st-key-retry_small button {{ background: {C['card']}; border: 1px solid {C['border']}; }}
.st-key-retry_small button p {{ color: {C['primary']}; font-size: 14px; font-weight: 600; }}
.fs-hint {{ font-size: 12px; color: {C['muted']}; text-align: center; margin-top: -4px; }}

.fs-guide h2 {{ font-size: 25px; line-height: 32px; margin: 8px 0 24px; color: {C['text']}; }}
.fs-tip {{ display: flex; gap: 12px; margin-bottom: 22px; }}
.fs-tipicon {{ width: 36px; height: 36px; border-radius: 10px; background: {C['mint']};
  display: flex; align-items: center; justify-content: center; flex: none; }}
.fs-tip b {{ display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; }}
.fs-tip p {{ font-size: 13px; color: {C['muted']}; line-height: 20px; margin: 0; }}
.fs-hr {{ height: 1px; background: {C['border']}; margin: 4px 0 24px; }}
.fs-note {{ display: flex; gap: 10px; font-size: 13px; color: {C['muted']}; line-height: 21px; }}

.fs-photo {{ width: 100%; height: 284px; object-fit: cover; display: block; }}
.fs-meta {{ display: flex; gap: 10px; align-items: center; padding: 18px; }}
.fs-meta b {{ display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; }}
.fs-meta span {{ font-size: 11px; color: {C['muted']}; }}
.fs-status {{ display: flex; gap: 8px; align-items: center; font-size: 12px; padding: 0 18px 18px; }}
.st-key-photo_card [data-testid="stElementContainer"]:has(button) {{ padding: 0 18px 18px; }}
.fs-status-out {{ display: flex; gap: 8px; align-items: center; font-size: 12px; color: {C['primary']}; margin: 18px 0; }}
.fs-cheer {{ background: {C['mint']}; border-radius: 10px; padding: 20px; color: {C['primary']}; }}
.fs-cheer h3 {{ font-size: 20px; margin: 0 0 8px; color: {C['primary']}; }}
.fs-cheer p {{ font-size: 13px; line-height: 21px; margin: 0; }}

.fs-recipe {{ background: {C['card']}; border: 1px solid {C['border']}; border-radius: 18px; padding: 28px; }}
.fs-label {{ display: flex; gap: 7px; align-items: center; font-size: 11px; font-weight: 600;
  letter-spacing: .04em; color: {C['primary']}; }}
.fs-dish {{ font-family: 'Lora', serif; font-size: 30px; line-height: 36px; margin: 12px 0; }}
.fs-warn {{ display: flex; gap: 9px; background: {C['warn_bg']}; color: {C['warn']}; border-radius: 8px;
  padding: 12px; font-size: 12px; line-height: 18px; }}
.fs-h2 {{ font-family: 'Lora', serif; font-size: 23px; line-height: 29px; margin: 24px 0 10px; }}
.fs-ing {{ display: grid; grid-template-columns: 1fr 1fr; column-gap: 24px; }}
.fs-ing div {{ display: flex; justify-content: space-between; align-items: center; font-size: 13px;
  padding: 10px 0; border-bottom: 1px solid {C['border']}; }}
.fs-ing b {{ color: {C['primary']}; font-weight: 600; }}
.fs-cook {{ display: flex; flex-direction: column; gap: 18px; margin-top: 18px; }}
.fs-cs {{ display: flex; gap: 12px; }}
.fs-num {{ width: 28px; height: 28px; border-radius: 99px; background: {C['mint']}; color: {C['primary']};
  font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex: none; }}
.fs-cs b {{ display: block; font-size: 14px; font-weight: 600; margin-bottom: 5px; }}
.fs-cs p {{ font-size: 13px; line-height: 20px; color: {C['muted']}; margin: 0; }}

.fs-errsym {{ width: 52px; height: 52px; border-radius: 16px; background: {C['warn_bg']};
  display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }}
.fs-errtitle {{ font-family: 'Lora', serif; font-size: 26px; line-height: 35px; margin: 0 0 16px; }}
.fs-errtext {{ font-size: 14px; color: {C['muted']}; line-height: 22px; margin: 0 0 24px; }}
.fs-advice {{ background: {C['bg']}; border-radius: 10px; padding: 18px; margin-bottom: 24px; }}
.fs-advice b {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 12px; }}
.fs-advice div {{ display: flex; gap: 9px; font-size: 13px; color: {C['muted']}; line-height: 18px; margin-bottom: 12px; }}
.fs-advice div:last-child {{ margin-bottom: 0; }}
.fs-formats {{ font-size: 12px; color: {C['muted']}; margin-top: 10px; }}

.st-key-nav {{ display: flex; justify-content: flex-end; padding: 14px 64px 0; }}
.st-key-nav button {{ background: transparent; border: 0; padding: 0; min-height: 0; width: auto;
  display: inline-flex; align-items: center; gap: 7px; }}
.st-key-nav button p {{ color: {C['muted']}; font-size: 13px; font-weight: 500; }}
.st-key-nav button:hover p {{ color: {C['primary']}; }}
.st-key-nav button::before {{ content: ""; width: 15px; height: 15px;
  background: {icon_uri('history', 15, C['muted'])} no-repeat center; }}

.fs-hist-count {{ font-size: 13px; color: {C['muted']}; margin-bottom: 18px; }}
.st-key-clear_hist button {{ height: 40px; border-radius: 9px; padding: 0 16px; font-size: 13px;
  font-weight: 600; border: 1px solid {C['border']}; background: {C['card']}; color: {C['warn']}; margin-bottom: 18px; }}
.st-key-clear_hist button p {{ color: {C['warn']}; font-size: 13px; font-weight: 600; }}
.st-key-clear_hist_btn button {{ display: inline-flex; align-items: center; gap: 8px; }}
.st-key-clear_hist_btn button::before {{ content: ""; width: 14px; height: 14px;
  background: {icon_uri('trash', 14, C['warn'])} no-repeat center; }}
.fs-hist-row {{ display: flex; gap: 16px; align-items: center; background: {C['card']};
  border: 1px solid {C['border']}; border-radius: 14px; padding: 14px; margin-bottom: 12px; }}
.fs-hist-thumb {{ width: 56px; height: 56px; border-radius: 10px; overflow: hidden; flex: none;
  background: {C['bg']}; display: flex; align-items: center; justify-content: center; }}
.fs-hist-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
.fs-hist-noimg {{ display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; }}
.fs-hist-info {{ flex: 1; min-width: 0; }}
.fs-hist-top {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
.fs-hist-top b {{ font-size: 14px; font-weight: 600; }}
.fs-hist-badge {{ font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 99px; }}
.fs-hist-meta {{ font-size: 12px; color: {C['muted']}; margin-top: 4px; }}
</style>
"""


def header_html() -> str:
    return f"""
<div class="fs-header">
  <div class="fs-brand">
    <div class="fs-mark">{icon('chef-hat', 23, '#fff')}</div>
    <span class="fs-name">FloodSnap Ai</span>
  </div>
  <span class="fs-desc">Ваш кулінарний помічник</span>
</div>"""


def footer_html() -> str:
    return """
<div class="fs-footer">
  <span>FloodSnap Ai · Артем Чікішев</span>
  <span>Рецепти від ШІ — орієнтир, а не точна копія.</span>
</div>"""


def intro_html(step2_active: bool, title: str, desc: str) -> str:
    s2 = "on" if step2_active else ""
    return f"""
<div class="fs-intro">
  <div class="fs-flow">
    <div class="fs-step on"><span class="fs-dot">1</span>Фото страви</div>
    <div class="fs-step {s2}"><span class="fs-line"></span><span class="fs-dot">2</span>Рецепт</div>
  </div>
  <div>
    <h1 class="fs-title">{title}</h1>
    <p class="fs-sub">{desc}</p>
  </div>
</div>"""


def file_meta(name: str, size: int) -> tuple[str, str]:
    ext = name.rsplit(".", 1)[-1].upper().replace("JPEG", "JPG")
    mb = f"{size / 1024 / 1024:.1f}".replace(".", ",")
    return name, f"{mb} МБ · {ext}"


def img_tag(data: bytes, name: str) -> str:
    mime = "image/png" if name.lower().endswith("png") else "image/jpeg"
    return f'<img class="fs-photo" src="data:{mime};base64,{base64.b64encode(data).decode()}">'


def meta_html(name: str, meta: str) -> str:
    return f"""<div class="fs-meta">{icon('image', 19, C['muted'])}
  <div><b>{name}</b><span>{meta}</span></div></div>"""


def init_state():
    ss = st.session_state
    ss.setdefault("screen", "upload")
    ss.setdefault("uploader_n", 0)
    ss.setdefault("photo", None)
    ss.setdefault("recipe", None)
    ss.setdefault("demo_note", None)
    ss.setdefault("source", None)
    preview = st.query_params.get("preview")
    if preview in ("recipe", "error") and not ss.get("_preview_done"):
        f = "pasta.jpg" if preview == "recipe" else "dish.jpg"
        data = (ASSETS / f).read_bytes()
        n, m = file_meta("pasta.jpg" if preview == "recipe" else "dish-photo.jpg", len(data))
        ss.photo, ss.recipe, ss.screen, ss._preview_done = (data, n, m), DEMO_RECIPE, preview, True


def reset():
    st.session_state.screen = "upload"
    st.session_state.photo = None
    st.session_state.recipe = None
    st.session_state.uploader_n += 1


def screen_upload():
    st.markdown(intro_html(False, "Що приготуємо сьогодні?",
                           "Покажіть фото страви — ми допоможемо відтворити її на вашій кухні."),
                unsafe_allow_html=True)
    if st.session_state.recipe and st.session_state.photo:
        with st.container(key="back"):
            if st.button("Повернутися до рецепта →", key="fwd_btn"):
                st.session_state.screen = "recipe"
                st.rerun()
    left, right = st.columns([640, 400], gap="large")
    with left:
        with st.container(key="upload_card"):
            st.markdown('<div class="fs-sec-head"><b>Фото вашої страви</b><span>JPG або PNG</span></div>',
                        unsafe_allow_html=True)
            stored = st.session_state.photo
            up = st.file_uploader("Фото", type=["jpg", "jpeg", "png"], label_visibility="collapsed",
                                  key=f"uploader_{st.session_state.uploader_n}")
            if up is not None:
                cur = (up.getvalue(), *file_meta(up.name, up.size))
            else:
                cur = stored
            if up is None and stored:
                d0, n0, m0 = stored
                mime = "image/png" if n0.lower().endswith("png") else "image/jpeg"
                st.markdown(f'<div class="fs-thumb"><img src="data:{mime};base64,{base64.b64encode(d0).decode()}">'
                            f'<div><b>{n0}</b><span>{m0} · буде використано це фото</span></div></div>',
                            unsafe_allow_html=True)
            with st.container(key="generate"):
                clicked = st.button("Згенерувати рецепт", disabled=cur is None, use_container_width=True)
            if cur is None:
                st.markdown('<div class="fs-hint">Спочатку завантажте фото страви</div>', unsafe_allow_html=True)
    with right:
        tips = [("sun", "Більше світла", "Знімайте при денному світлі, без сильних тіней."),
                ("focus", "Страва у фокусі", "Нехай у кадрі буде одна страва, яку добре видно."),
                ("scan-line", "Без зайвих деталей", "Уникайте розмиття, написів і предметів перед тарілкою.")]
        tips_html = "".join(
            f'<div class="fs-tip"><div class="fs-tipicon">{icon(i, 19)}</div><div><b>{t}</b><p>{d}</p></div></div>'
            for i, t, d in tips)
        st.markdown(f"""
<div class="fs-guide">
  <h2>Гарне фото — кращий рецепт</h2>
  {tips_html}
  <div class="fs-hr"></div>
  <div class="fs-note">{icon('sparkles', 18, C['muted'])}
    <span>ШІ запропонує приблизний рецепт. Інгредієнти на фото можуть відрізнятися від справжніх.</span></div>
</div>""", unsafe_allow_html=True)

    if clicked and cur is not None:
        data, name, meta = cur
        with st.spinner("Аналізуємо фото…"):
            recipe = generate_recipe(data, mime_of(name))
        st.session_state.photo = (data, name, meta)
        st.session_state.recipe = recipe
        st.session_state.screen = "recipe" if recipe else "error"
        st.rerun()


def back_button():
    with st.container(key="back"):
        if st.button("← Назад", key="back_btn"):
            st.session_state.screen = "upload"
            st.rerun()


def screen_recipe():
    back_button()
    data, name, meta = st.session_state.photo
    r = st.session_state.recipe
    st.markdown("<style>.st-key-workspace [data-testid='stHorizontalBlock']{gap:28px}</style>"
                + intro_html(True, "З фото — до вашого столу",
                             "Рецепт готовий. Підготуйте інгредієнти та почнімо готувати."),
                unsafe_allow_html=True)
    if st.session_state.get("demo_note"):
        st.markdown(f'<div class="fs-warn" style="margin-bottom:20px">{icon("info", 16, C["warn"])}'
                    f'<span>{st.session_state.demo_note}</span></div>', unsafe_allow_html=True)
    left, right = st.columns([320, 724], gap="large")
    with left:
        with st.container(key="photo_card"):
            st.markdown(img_tag(data, name) + meta_html(name, meta), unsafe_allow_html=True)
            with st.container(key="retry_small"):
                if st.button("Завантажити інше фото", use_container_width=True):
                    reset(); st.rerun()
        st.markdown(f"""
<div class="fs-status-out">{icon('circle-check', 17)}<span>Фото проаналізовано{(' · ' + st.session_state.source) if st.session_state.get('source') else ''}</span></div>
<div class="fs-cheer"><h3>У вас усе вийде</h3>
<p>Прочитайте всі кроки перед початком і тримайте потрібні продукти під рукою.</p></div>""",
                    unsafe_allow_html=True)
    with right:
        ing = "".join(f"<div><span>{n}</span><b>{q}</b></div>" for n, q in r["ingredients"])
        steps = "".join(
            f'<div class="fs-cs"><div class="fs-num">{i}</div><div><b>{t}</b><p>{d}</p></div></div>'
            for i, (t, d) in enumerate(r["steps"], 1))
        st.markdown(f"""
<div class="fs-recipe">
  <div class="fs-label">{icon('sparkles', 15)}РЕЦЕПТ ЗА ВАШИМ ФОТО</div>
  <div class="fs-dish">{r['name']}</div>
  <div class="fs-warn">{icon('info', 16, C['warn'])}<span>Це приблизний рецепт від ШІ. Страву може бути визначено неточно; склад і кількості можуть відрізнятися.</span></div>
  <div class="fs-h2">Інгредієнти</div>
  <div class="fs-ing">{ing}</div>
  <div class="fs-h2">Як приготувати</div>
  <div class="fs-cook">{steps}</div>
</div>""", unsafe_allow_html=True)


def screen_error():
    back_button()
    data, name, meta = st.session_state.photo
    st.markdown("<style>.st-key-workspace [data-testid='stHorizontalBlock']{gap:28px}</style>"
                + intro_html(False, "Спробуймо з іншим фото",
                             "Цього разу не вдалося розпізнати страву. Ми допоможемо почати ще раз."),
                unsafe_allow_html=True)
    left, right = st.columns([320, 724], gap="large")
    with left:
        with st.container(key="error_photo"):
            st.markdown(img_tag(data, name) + meta_html(name, meta)
                        + f'<div class="fs-status" style="color:{C["warn"]}">{icon("circle-alert", 16, C["warn"])}'
                          '<span>Страву не розпізнано</span></div>', unsafe_allow_html=True)
    with right:
        with st.container(key="error_card"):
            tips = ["Зніміть страву ближче й при гарному освітленні.",
                    "Переконайтеся, що фото чітке та без розмиття.",
                    "Залиште в кадрі одну тарілку зі стравою."]
            tips_html = "".join(f"<div>{icon('check', 15)}<span>{t}</span></div>" for t in tips)
            st.markdown(f"""
<div class="fs-errsym">{icon('scan-line', 27, C['warn'])}</div>
<div class="fs-errtitle">Не вдалося визначити страву. Спробуйте завантажити інше фото</div>
<p class="fs-errtext">На знімку замало чітких деталей. Рецепт не створено, щоб не вводити вас в оману.</p>
<div class="fs-advice"><b>Для наступної спроби</b>{tips_html}</div>""", unsafe_allow_html=True)
            with st.container(key="retry"):
                if st.button("Завантажити інше фото", use_container_width=True):
                    reset(); st.rerun()
            st.markdown('<div class="fs-formats">Виберіть нове фото у форматі JPG або PNG</div>',
                        unsafe_allow_html=True)


def screen_history():
    with st.container(key="back"):
        if st.button("← Назад", key="hist_back_btn"):
            st.session_state.screen = "upload"
            st.rerun()
    st.markdown(intro_html(False, "Історія запитів до ШІ",
                           "Усі фото, надіслані на розпізнавання, та результат кожного запиту."),
                unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.markdown('<div class="fs-hint" style="text-align:left">Поки порожньо — перший запит потрапить сюди одразу після аналізу фото.</div>',
                    unsafe_allow_html=True)
        return

    st.markdown(f'<div class="fs-hist-count">Усього запитів: {len(history)}</div>', unsafe_allow_html=True)

    st.session_state.setdefault("confirm_clear_history", False)
    with st.container(key="clear_hist"):
        if st.session_state.confirm_clear_history:
            st.markdown(f'<div class="fs-warn" style="margin-bottom:12px">{icon("circle-alert", 16, C["warn"])}'
                        f'<span>Видалити всю історію без можливості відновлення?</span></div>', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Так, видалити", key="confirm_clear_hist", use_container_width=True):
                    HISTORY_FILE.unlink(missing_ok=True)
                    st.session_state.confirm_clear_history = False
                    st.rerun()
            with c2:
                if st.button("Скасувати", key="cancel_clear_hist", use_container_width=True):
                    st.session_state.confirm_clear_history = False
                    st.rerun()
        else:
            if st.button("Очистити історію", key="clear_hist_btn"):
                st.session_state.confirm_clear_history = True
                st.rerun()

    badge_map = {
        "success": ("Розпізнано", C["primary"], C["mint"]),
        "demo": ("Демо-режим", C["warn"], C["warn_bg"]),
        "no_dish": ("Не розпізнано", C["warn"], C["warn_bg"]),
    }
    rows = []
    for h in history:
        thumb = (f'<img src="data:image/jpeg;base64,{h["thumb"]}">' if h.get("thumb")
                  else f'<div class="fs-hist-noimg">{icon("image", 20, C["muted"])}</div>')
        label, fg, bg = badge_map.get(h.get("status"), ("Невідомо", C["muted"], C["off_bg"]))
        dish = h.get("dish") or ("Демо-рецепт" if h.get("status") == "demo" else "Страву не визначено")
        model = h.get("model") or "—"
        rows.append(f"""
<div class="fs-hist-row">
  <div class="fs-hist-thumb">{thumb}</div>
  <div class="fs-hist-info">
    <div class="fs-hist-top"><b>{dish}</b><span class="fs-hist-badge" style="color:{fg};background:{bg}">{label}</span></div>
    <div class="fs-hist-meta">{h.get('ts', '—')} · модель: {model}</div>
  </div>
</div>""")
    st.markdown("".join(rows), unsafe_allow_html=True)


st.set_page_config(page_title="FloodSnap Ai", page_icon="🍝", layout="wide")
st.markdown(base_css(), unsafe_allow_html=True)
init_state()
st.markdown(header_html(), unsafe_allow_html=True)
if st.session_state.screen != "history":
    with st.container(key="nav"):
        if st.button("Історія запитів", key="history_nav_btn"):
            st.session_state.screen = "history"
            st.rerun()
with st.container(key="workspace"):
    {"upload": screen_upload, "recipe": screen_recipe, "error": screen_error,
     "history": screen_history}[st.session_state.screen]()
st.markdown(footer_html(), unsafe_allow_html=True)