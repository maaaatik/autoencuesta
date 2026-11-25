import io
import os
import subprocess
import time
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

st.set_page_config(
    page_title="Encuestas automaticas by Matik",
    page_icon="◼️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ESTILO MANGA / ANIME JAPONÉS EN BLANCO Y NEGRO ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+JP:wght@400;700;900&display=swap');

    :root {
        --bg-primary: #FFFFFF;
        --bg-secondary: #FAFAFA;
        --text-primary: #0A0A0A;
        --text-secondary: #404040;
        --border-strong: #0A0A0A;
    }

    /* Fondo con trama sutil de semitono manga (screentone dots) */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
        background-image: radial-gradient(#D4D4D4 0.85px, transparent 0.85px) !important;
        background-size: 16px 16px !important;
        color: var(--text-primary) !important;
    }

    header[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.94) !important;
        border-bottom: 2px solid #0A0A0A !important;
    }

    .block-container {
        max-width: 960px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
    }

    /* Panel Principal estilo Viñeta Manga */
    .manga-hero {
        position: relative;
        background-color: #FFFFFF;
        border: 2.5px solid #0A0A0A;
        box-shadow: 6px 6px 0px #0A0A0A;
        padding: 1.75rem 2rem;
        margin-bottom: 2.2rem;
        overflow: hidden;
    }

    /* Líneas cinéticas sutiles en la esquina */
    .manga-hero::before {
        content: "";
        position: absolute;
        top: -20px;
        right: -20px;
        width: 220px;
        height: 220px;
        background: repeating-conic-gradient(
            from 0deg,
            rgba(10, 10, 10, 0.05) 0deg 2deg,
            transparent 2deg 8deg
        );
        border-radius: 50%;
        pointer-events: none;
    }

    .manga-top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1.5px solid #0A0A0A;
        padding-bottom: 0.6rem;
        margin-bottom: 1rem;
    }

    .manga-kicker {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #0A0A0A;
    }

    .manga-jp-tag {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        background-color: #0A0A0A;
        color: #FFFFFF;
        padding: 2px 10px;
    }

    .manga-hero-grid {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.5rem;
    }

    .manga-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #0A0A0A;
        line-height: 1.1;
        margin: 0;
        text-transform: uppercase;
    }

    .manga-jp-sub {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        color: #525252;
        margin-top: 0.35rem;
        letter-spacing: 0.08em;
    }

    .manga-subtitle {
        font-size: 0.94rem;
        color: #262626;
        margin-top: 0.75rem;
        line-height: 1.5;
        max-width: 640px;
    }

    /* Sello Hanko Japonés */
    .hanko-stamp {
        flex-shrink: 0;
        width: 68px;
        height: 68px;
        border: 2.5px solid #0A0A0A;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Noto Sans JP', sans-serif;
        font-weight: 900;
        font-size: 1.05rem;
        line-height: 1.05;
        color: #0A0A0A;
        background-color: #FFFFFF;
        transform: rotate(-4deg);
        box-shadow: 3px 3px 0px #0A0A0A;
        user-select: none;
    }

    /* Viñetas para cada sección */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        padding: 1.35rem !important;
        box-shadow: 5px 5px 0px #0A0A0A !important;
        margin-bottom: 1.25rem !important;
    }

    /* Encabezados de sección estilo capítulo de manga */
    .chapter-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        border-bottom: 1.5px solid #0A0A0A;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .chapter-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        background-color: #0A0A0A;
        color: #FFFFFF;
        padding: 3px 8px;
    }
    .chapter-title {
        font-size: 1.12rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        text-transform: uppercase;
        color: #0A0A0A;
    }
    .chapter-jp {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #525252;
        margin-left: auto;
    }

    /* Inputs de texto estilo cuadro de diálogo */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #0A0A0A !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        padding: 0.65rem 0.85rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
    }
    .stTextInput input:focus {
        box-shadow: 3px 3px 0px #0A0A0A !important;
        outline: none !important;
    }

    /* Botones primarios estilo acción manga */
    .stButton > button[kind="primary"], .stButton > button {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        padding: 0.6rem 1.3rem !important;
        box-shadow: 3px 3px 0px #737373 !important;
        transition: transform 0.1s ease, box-shadow 0.1s ease !important;
    }
    .stButton > button:hover {
        background-color: #FFFFFF !important;
        color: #0A0A0A !important;
        box-shadow: 4px 4px 0px #0A0A0A !important;
        transform: translate(-1px, -1px);
    }

    /* Botones de descarga */
    .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #0A0A0A !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        padding: 0.55rem 1.1rem !important;
        width: 100%;
        box-shadow: 3px 3px 0px #0A0A0A !important;
        transition: all 0.12s ease !important;
    }
    .stDownloadButton > button:hover {
        background-color: #0A0A0A !important;
        color: #FFFFFF !important;
    }

    /* File Uploader */
    [data-testid="stFileUploader"] section {
        background-color: #FAFAFA !important;
        border: 2px dashed #0A0A0A !important;
        border-radius: 0px !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #0A0A0A !important;
    }

    /* Alertas estilo globo de texto manga */
    [data-testid="stAlert"] {
        background-color: #FFFFFF !important;
        color: #0A0A0A !important;
        border: 2px solid #0A0A0A !important;
        border-left: 6px solid #0A0A0A !important;
        border-radius: 0px !important;
        font-weight: 500 !important;
    }

    /* Barra de progreso */
    .stProgress > div > div > div > div {
        background-color: #0A0A0A !important;
    }

    /* Badges de tipo */
    .type-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        background-color: #0A0A0A;
        color: #FFFFFF;
        padding: 2px 7px;
        margin-left: 6px;
        vertical-align: middle;
    }

    /* Footer */
    .matik-footer {
        margin-top: 2.5rem;
        padding: 1rem 1.25rem;
        background-color: #0A0A0A;
        color: #FFFFFF;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', 'Noto Sans JP', monospace;
        letter-spacing: 0.08em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def asegurar_chromium():
    """Instala el binario de Chromium en Streamlit Cloud si aún no está presente."""
    try:
        with sync_playwright() as p:
            exe = p.chromium.executable_path
            if os.path.exists(exe):
                return True
    except Exception:
        pass

    subprocess.run(["playwright", "install", "chromium"], check=True)
    return True


asegurar_chromium()


def detectar_plataforma(url: str) -> str:
    u = url.lower()
    if "forms.office.com" in u or "forms.cloud.microsoft" in u:
        return "microsoft"
    if "docs.google.com/forms" in u or "forms.gle" in u:
        return "google"
    return "desconocida"


def _extraer_opciones_ms(item, role_name: str) -> list[str]:
    opciones = []
    els = item.get_by_role(role_name)
    for i in range(els.count()):
        el = els.nth(i)
        label = el.get_attribute("aria-label") or el.get_attribute("value") or el.inner_text()
        if not label or not label.strip():
            parent_text = el.locator("xpath=..").inner_text()
            if parent_text:
                label = parent_text.splitlines()[0]
        if label:
            clean_lbl = label.strip()
            if clean_lbl and clean_lbl not in opciones:
                opciones.append(clean_lbl)
    return opciones


def inspeccionar_microsoft_forms(page) -> list[dict]:
    preguntas_map = {}

    for _ in range(15):
        items = page.locator("[data-automation-id='questionItem']")
        count = items.count()
        for idx in range(count):
            item = items.nth(idx)
            if not item.is_visible():
                continue

            title_el = item.locator("[data-automation-id='questionTitle']")
            if title_el.count() > 0:
                texto = title_el.first.inner_text().strip()
            else:
                lineas = [l.strip() for l in item.inner_text().splitlines() if l.strip()]
                texto = lineas[0] if lineas else f"Pregunta {len(preguntas_map) + 1}"

            texto_limpio = texto.lstrip("0123456789. ").rstrip("* ").strip()
            if not texto_limpio:
                texto_limpio = texto

            if texto_limpio in preguntas_map:
                continue

            radios = item.get_by_role("radio")
            checkboxes = item.get_by_role("checkbox")
            inputs = item.locator("input:not([type='radio']):not([type='checkbox']), textarea")

            if radios.count() > 0:
                opciones = _extraer_opciones_ms(item, "radio")
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "radio",
                    "opciones": opciones,
                }
            elif checkboxes.count() > 0:
                opciones = _extraer_opciones_ms(item, "checkbox")
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "checkbox",
                    "opciones": opciones,
                }
            elif inputs.count() > 0:
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "texto",
                    "opciones": [],
                }

        btn_siguiente = page.locator("button[data-automation-id='nextButton'], button:has-text('Siguiente'), button:has-text('Next')")
        if btn_siguiente.count() > 0 and btn_siguiente.first.is_visible():
            for idx in range(items.count()):
                item = items.nth(idx)
                if not item.is_visible():
                    continue
                radios = item.get_by_role("radio")
                if radios.count() > 0:
                    radios.first.click(force=True)
                checkboxes = item.get_by_role("checkbox")
                if checkboxes.count() > 0:
                    checkboxes.first.click(force=True)
                inputs = item.locator("input:not([type='radio']):not([type='checkbox']), textarea")
                if inputs.count() > 0:
                    inputs.first.fill("1")

            time.sleep(0.3)
            btn_siguiente.first.click()
            time.sleep(1.2)
        else:
            break

    return list(preguntas_map.values())


def inspeccionar_google_forms(page) -> list[dict]:
    preguntas_map = {}

    for _ in range(15):
        items = page.locator("div[role='listitem']")
        count = items.count()
        for idx in range(count):
            item = items.nth(idx)
            if not item.is_visible():
                continue

            heading = item.locator("[role='heading']")
            if heading.count() == 0:
                continue
            texto_limpio = heading.first.inner_text().replace("*", "").strip()
            if not texto_limpio or texto_limpio in preguntas_map:
                continue

            radios = item.locator("[role='radio']")
            checkboxes = item.locator("[role='checkbox']")
            inputs = item.locator("input[type='text'], input[type='number'], textarea")

            if radios.count() > 0:
                opciones = []
                for r_i in range(radios.count()):
                    val = radios.nth(r_i).get_attribute("data-value") or radios.nth(r_i).get_attribute("aria-label")
                    if val and val != "__other_option__":
                        opciones.append(val.strip())
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "radio",
                    "opciones": opciones,
                }
            elif checkboxes.count() > 0:
                opciones = []
                for c_i in range(checkboxes.count()):
                    val = checkboxes.nth(c_i).get_attribute("data-answer-value") or checkboxes.nth(c_i).get_attribute("aria-label")
                    if val and val != "__other_option__":
                        opciones.append(val.strip())
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "checkbox",
                    "opciones": opciones,
                }
            elif inputs.count() > 0:
                preguntas_map[texto_limpio] = {
                    "pregunta": texto_limpio,
                    "tipo": "texto",
                    "opciones": [],
                }

        btn_siguiente = page.locator("div[role='button']").filter(has_text="Siguiente")
        if btn_siguiente.count() > 0 and btn_siguiente.first.is_visible():
            for idx in range(items.count()):
                item = items.nth(idx)
                if not item.is_visible():
                    continue
                radios = item.locator("[role='radio']")
                if radios.count() > 0:
                    radios.first.click()
                inputs = item.locator("input[type='text'], input[type='number'], textarea")
                if inputs.count() > 0:
                    inputs.first.fill("1")
            btn_siguiente.first.click()
            time.sleep(1.0)
        else:
            break

    return list(preguntas_map.values())


def extraer_esquema(url: str) -> tuple[str, list[dict]]:
    plataforma = detectar_plataforma(url)
    if plataforma == "desconocida":
        raise ValueError("URL no reconocida. Usa un enlace de Microsoft Forms o Google Forms.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(1.5)

        if plataforma == "microsoft":
            page.wait_for_selector("[data-automation-id='questionItem']", timeout=20000)
            esquema = inspeccionar_microsoft_forms(page)
        else:
            page.wait_for_selector("div[role='listitem']", timeout=20000)
            esquema = inspeccionar_google_forms(page)

        browser.close()
    return plataforma, esquema


def llenar_pagina_microsoft(page, fila: dict, esquema: list[dict]):
    for q in esquema:
        preg = q["pregunta"]
        valor = str(fila.get(preg, "")).strip()
        if not valor or valor.lower() == "nan":
            continue

        item = page.locator("[data-automation-id='questionItem']").filter(has_text=preg)
        if item.count() == 0 or not item.first.is_visible():
            continue

        if q["tipo"] == "radio":
            radio = item.first.get_by_role("radio", name=valor, exact=True)
            if radio.count() > 0:
                radio.first.click()
        elif q["tipo"] == "checkbox":
            for opcion in [o.strip() for o in valor.split(";") if o.strip()]:
                chk = item.first.get_by_role("checkbox", name=opcion, exact=True)
                if chk.count() > 0:
                    chk.first.click()
        else:
            campo = item.first.locator("input:not([type='radio']):not([type='checkbox']), textarea").first
            if campo.count() > 0:
                campo.fill(valor)


def llenar_pagina_google(page, fila: dict, esquema: list[dict]):
    for q in esquema:
        preg = q["pregunta"]
        valor = str(fila.get(preg, "")).strip()
        if not valor or valor.lower() == "nan":
            continue

        item = page.locator("div[role='listitem']").filter(has_text=preg)
        if item.count() == 0 or not item.first.is_visible():
            continue

        if q["tipo"] == "radio":
            radio = item.first.locator(f"[role='radio'][data-value='{valor}'], [role='radio'][aria-label='{valor}']")
            if radio.count() > 0:
                radio.first.click()
        elif q["tipo"] == "checkbox":
            for opcion in [o.strip() for o in valor.split(";") if o.strip()]:
                chk = item.first.locator(f"[role='checkbox'][data-answer-value='{opcion}'], [role='checkbox'][aria-label='{opcion}']")
                if chk.count() > 0:
                    chk.first.click()
        else:
            campo = item.first.locator("input[type='text'], input[type='number'], textarea").first
            if campo.count() > 0:
                campo.fill(valor)


def ejecutar_envios(url: str, plataforma: str, esquema: list[dict], registros: list[dict], delay: float):
    enviadas = 0
    errores = []
    barra = st.progress(0)
    estado = st.empty()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()

        for i, fila in enumerate(registros, start=1):
            estado.info(f"Procesando envío {i} de {len(registros)}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)

                if plataforma == "microsoft":
                    page.wait_for_selector("[data-automation-id='questionItem']", timeout=20000)
                    for _ in range(15):
                        llenar_pagina_microsoft(page, fila, esquema)
                        time.sleep(0.3)

                        btn_enviar = page.locator("button[data-automation-id='submitButton'], button:has-text('Enviar'), button:has-text('Submit')")
                        if btn_enviar.count() > 0 and btn_enviar.first.is_visible():
                            btn_enviar.first.click()
                            break

                        btn_sig = page.locator("button[data-automation-id='nextButton'], button:has-text('Siguiente'), button:has-text('Next')")
                        if btn_sig.count() > 0 and btn_sig.first.is_visible():
                            btn_sig.first.click()
                            time.sleep(0.8)
                        else:
                            break
                    page.wait_for_selector("text=Enviar otra respuesta", timeout=20000)

                else:
                    page.wait_for_selector("div[role='listitem']", timeout=20000)
                    for _ in range(15):
                        llenar_pagina_google(page, fila, esquema)
                        time.sleep(0.3)

                        btn_enviar = page.locator("div[role='button']").filter(has_text="Enviar")
                        if btn_enviar.count() > 0 and btn_enviar.first.is_visible():
                            btn_enviar.first.click()
                            break

                        btn_sig = page.locator("div[role='button']").filter(has_text="Siguiente")
                        if btn_sig.count() > 0 and btn_sig.first.is_visible():
                            btn_sig.first.click()
                            time.sleep(0.8)
                        else:
                            break
                    page.wait_for_selector("text=Enviar otra respuesta", timeout=20000)

                enviadas += 1
                time.sleep(delay)

            except PlaywrightTimeoutError:
                errores.append(f"Fila {i}: Tiempo de espera agotado (revisa campos obligatorios o valores mal escritos).")
            except Exception as e:
                errores.append(f"Fila {i}: {e}")

            barra.progress(i / len(registros))

        browser.close()

    estado.empty()
    return enviadas, errores


# --- ENCABEZADO MANGA / ANIME MONOCROMÁTICO ---
st.markdown(
    """
    <div class="manga-hero">
        <div class="manga-top-bar">
            <span class="manga-kicker">SYSTEM // FORMS AUTOMATION ENGINE</span>
            <span class="manga-jp-tag">自動アンケート // マティク</span>
        </div>
        <div class="manga-hero-grid">
            <div>
                <h1 class="manga-title">Encuestas automaticas by Matik</h1>
                <div class="manga-jp-sub">マティク・オートメーション — MICROSOFT FORMS &amp; GOOGLE FORMS</div>
                <p class="manga-subtitle">
                    Escanea la estructura de cualquier encuesta, obtén su plantilla exacta y ejecuta envíos masivos de forma automatizada.
                </p>
            </div>
            <div class="hanko-stamp">
                <span>マテ</span>
                <span>ィク</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "esquema" not in st.session_state:
    st.session_state.esquema = None
    st.session_state.plataforma = None
    st.session_state.url = ""

# --- CAPÍTULO 01 ---
with st.container(border=True):
    st.markdown(
        """
        <div class="chapter-header">
            <span class="chapter-num">CH.01</span>
            <span class="chapter-title">Enlace del formulario</span>
            <span class="chapter-jp">リンク入力</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    url_input = st.text_input(
        "URL pública de la encuesta",
        placeholder="https://forms.cloud.microsoft/... o https://docs.google.com/forms/...",
    )

    if st.button("Extraer preguntas automáticamente", type="primary"):
        if not url_input.strip():
            st.warning("Ingresa un enlace válido primero.")
        else:
            with st.spinner("Escaneando paneles y secciones del formulario..."):
                try:
                    plat, esq = extraer_esquema(url_input.strip())
                    st.session_state.esquema = esq
                    st.session_state.plataforma = plat
                    st.session_state.url = url_input.strip()
                    st.success(f"Plataforma detectada: **{plat.upper()}** — **{len(esq)}** preguntas extraídas correctamente.")
                except Exception as e:
                    st.error(f"No se pudo inspeccionar el formulario: {e}")

if st.session_state.esquema:
    esquema = st.session_state.esquema

    with st.expander("Estructura y opciones detectadas // 質問リスト", expanded=True):
        for idx, q in enumerate(esquema, 1):
            opts = ", ".join(q["opciones"]) if q["opciones"] else "Campo abierto / numérico"
            st.markdown(
                f"**{idx:02d}. {q['pregunta']}** <span class='type-badge'>{q['tipo'].upper()}</span><br>"
                f"<span style='color:#404040; font-size:0.86rem;'>Opciones: {opts}</span>",
                unsafe_allow_html=True,
            )

    # --- CAPÍTULO 02 ---
    with st.container(border=True):
        st.markdown(
            """
            <div class="chapter-header">
                <span class="chapter-num">CH.02</span>
                <span class="chapter-title">Plantilla de datos</span>
                <span class="chapter-jp">テンプレート</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Descarga el formato exacto con las columnas vinculadas a cada pregunta.")
        columnas = [q["pregunta"] for q in esquema]
        fila_ejemplo = {
            q["pregunta"]: (q["opciones"][0] if q["opciones"] else "Ejemplo")
            for q in esquema
        }
        df_plantilla = pd.DataFrame([fila_ejemplo], columns=columnas)

        buffer_xlsx = io.BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as writer:
            df_plantilla.to_excel(writer, index=False, sheet_name="Respuestas")
            info_opciones = [
                {"Pregunta": q["pregunta"], "Tipo": q["tipo"], "Opciones válidas": " | ".join(q["opciones"])}
                for q in esquema
            ]
            pd.DataFrame(info_opciones).to_excel(writer, index=False, sheet_name="Opciones_Validas")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Descargar plantilla Excel (.xlsx)",
                data=buffer_xlsx.getvalue(),
                file_name="plantilla_encuesta_matik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with col2:
            st.download_button(
                label="Descargar plantilla CSV (.csv)",
                data=df_plantilla.to_csv(index=False).encode("utf-8-sig"),
                file_name="plantilla_encuesta_matik.csv",
                mime="text/csv",
            )

    # --- CAPÍTULO 03 ---
    with st.container(border=True):
        st.markdown(
            """
            <div class="chapter-header">
                <span class="chapter-num">CH.03</span>
                <span class="chapter-title">Carga y ejecución masiva</span>
                <span class="chapter-jp">自動送信</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        archivo = st.file_uploader("Archivo de respuestas (.xlsx o .csv)", type=["xlsx", "csv"])
        delay = st.slider("Intervalo entre envíos (segundos)", min_value=0.5, max_value=5.0, value=1.2, step=0.1)

        if archivo is not None:
            if archivo.name.endswith(".csv"):
                df_resp = pd.read_csv(archivo)
            else:
                df_resp = pd.read_excel(archivo, sheet_name=0)

            st.caption(f"Vista previa — **{len(df_resp)}** registros listos para procesar:")
            st.dataframe(df_resp.head(10), use_container_width=True)

            if st.button("Iniciar envío masivo", type="primary"):
                registros = df_resp.to_dict(orient="records")
                enviadas, errores = ejecutar_envios(
                    st.session_state.url,
                    st.session_state.plataforma,
                    esquema,
                    registros,
                    delay,
                )
                st.success(f"Ejecución completada: **{enviadas}/{len(registros)}** respuestas enviadas.")
                if errores:
                    with st.expander("Registro de incidencias"):
                        for err in errores:
                            st.error(err)

st.markdown(
    """
    <div class="matik-footer">
        <span>ENCUESTAS AUTOMATICAS BY MATIK // マティク</span>
        <span>MONOCHROME MANGA EDITION</span>
    </div>
    """,
    unsafe_allow_html=True,
)
