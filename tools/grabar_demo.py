"""Graba docs/img/demo.gif: login, escaneo de puertos, fuerza bruta SSH e histórico.

Necesita el laboratorio y el frontend levantados:
    cd infra && docker compose up -d        (backend en :8000)
    cd frontend && npm run dev              (frontend en :5173)

Uso (desde la raíz del repo, con Playwright y Pillow instalados):
    python tools/grabar_demo.py
    VECTORRT_USERNAME=... VECTORRT_PASSWORD=... python tools/grabar_demo.py   # si cambiaste las credenciales

El GIF va a cámara rápida: se toma una captura cada ~0,3 s y cada una dura 0,1 s.
"""

from __future__ import annotations

import io
import os
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img" / "demo.gif"
URL = os.environ.get("VECTORRT_URL", "http://localhost:5173")
USER = os.environ.get("VECTORRT_USERNAME", "admin")
PASSWORD = os.environ.get("VECTORRT_PASSWORD", "changeme")

VIEWPORT = {"width": 1280, "height": 860}
GIF_WIDTH = 880
SAMPLE_EVERY = 0.3   # segundos reales entre capturas
FRAME_MS = 100       # duración de cada captura en el GIF
MAX_WAIT = 120       # segundos máximos por ataque

frames: list[tuple[Image.Image, int]] = []


def snap(page, ms: int = FRAME_MS) -> None:
    frames.append((Image.open(io.BytesIO(page.screenshot(type="png"))).convert("RGB"), ms))


def hold(page, ms: int) -> None:
    page.wait_for_timeout(200)
    snap(page, ms)


def run_attack(page, target_ip: str, button: str) -> None:
    page.select_option("#target", target_ip)
    hold(page, 700)
    page.get_by_role("button", name=button).click()
    page.get_by_text("Ejecutando…").scroll_into_view_if_needed()
    start = time.perf_counter()
    while time.perf_counter() - start < MAX_WAIT:
        tick = time.perf_counter()
        snap(page)
        if page.get_by_text("Finalizado", exact=True).count() or page.get_by_text("Error", exact=True).count():
            break
        page.wait_for_timeout(max(0, int((SAMPLE_EVERY - (time.perf_counter() - tick)) * 1000)))
    else:
        print(f"  aviso: '{button}' no terminó en {MAX_WAIT} s")
    hold(page, 2500)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        try:
            page.goto(URL)
        except Exception:
            sys.exit(f"No responde {URL}: levanta el frontend con `npm run dev` en frontend/")

        # Login
        page.wait_for_selector("#username")
        hold(page, 900)
        page.fill("#username", USER)
        snap(page, 300)
        page.fill("#password", PASSWORD)
        snap(page, 500)
        page.get_by_role("button", name="Entrar").click()
        try:
            page.wait_for_selector("#target", timeout=10_000)
        except Exception:
            sys.exit("No se pudo iniciar sesión: revisa VECTORRT_USERNAME / VECTORRT_PASSWORD y que el backend esté en :8000")
        page.wait_for_function("document.querySelectorAll('#target option').length > 1")
        hold(page, 1200)

        # Ataques
        run_attack(page, "10.10.10.12", "Escaneo de puertos")   # multi-target
        page.evaluate("window.scrollTo(0, 0)")
        run_attack(page, "10.10.10.10", "Fuerza bruta SSH")     # ssh-target

        # Histórico
        page.get_by_text("Histórico", exact=True).scroll_into_view_if_needed()
        hold(page, 1200)
        detalle = page.get_by_role("button", name="ver detalle").first
        if detalle.count():
            detalle.click()
            detalle.scroll_into_view_if_needed()
            hold(page, 3500)
        browser.close()

    height = round(VIEWPORT["height"] * GIF_WIDTH / VIEWPORT["width"])
    images = [img.resize((GIF_WIDTH, height), Image.Resampling.LANCZOS) for img, _ in frames]
    picks = [images[0], images[len(images) // 3], images[2 * len(images) // 3], images[-1]]
    montage = Image.new("RGB", (GIF_WIDTH, height * len(picks)))
    for i, img in enumerate(picks):
        montage.paste(img, (0, i * height))
    palette = montage.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    paletted = [img.quantize(palette=palette, dither=Image.Dither.NONE) for img in images]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    paletted[0].save(OUT, save_all=True, append_images=paletted[1:], duration=[ms for _, ms in frames],
                     loop=0, optimize=True, disposal=1)
    print(f"{OUT.relative_to(ROOT)} · {len(frames)} fotogramas · {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
