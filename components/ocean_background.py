"""Animated Ocean Background Component.

Renders the animated deep-sea life behind everything:
light rays, drifting glow blobs, waves, kelp, bubbles, plankton, swimming fish,
sea turtle, jellyfish, and pufferfish.
Spec: design/nemo-ui-design.dc.html
"""

import streamlit as st

OCEAN_SVG_DEFS = """<svg width="0" height="0" style="position:absolute;" aria-hidden="true" focusable="false">
<defs>
<linearGradient id="nmShade" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#000" stop-opacity=".55"/>
<stop offset=".42" stop-color="#000" stop-opacity=".05"/>
<stop offset=".62" stop-color="#fff" stop-opacity=".05"/>
<stop offset="1" stop-color="#fff" stop-opacity=".45"/>
</linearGradient>
<pattern id="nmScales" width="5" height="4" patternUnits="userSpaceOnUse"><path d="M0 4 Q2.5 0 5 4" stroke="#000" stroke-opacity=".25" stroke-width=".55" fill="none"/></pattern>
<pattern id="nmScalesL" width="10" height="8" patternUnits="userSpaceOnUse"><path d="M0 8 Q5 0 10 8" stroke="#5a1f04" stroke-opacity=".28" stroke-width="1" fill="none"/></pattern>
<radialGradient id="nmGloss" cx=".4" cy=".25" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="nmClown" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C8460F"/><stop offset=".4" stop-color="#F77B24"/><stop offset=".75" stop-color="#FF9A45"/><stop offset="1" stop-color="#FFC27A"/></linearGradient>
<linearGradient id="nmBand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c3ccd3"/><stop offset=".5" stop-color="#ffffff"/><stop offset="1" stop-color="#e3e9ee"/></linearGradient>
<linearGradient id="nmShellG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6d8a45"/><stop offset=".6" stop-color="#3b5a32"/><stop offset="1" stop-color="#22372a"/></linearGradient>
<linearGradient id="nmSkinG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7d9a5a"/><stop offset="1" stop-color="#46663f"/></linearGradient>
<radialGradient id="nmPuffBody" cx=".45" cy=".35" r=".8"><stop offset="0" stop-color="#f8e08e"/><stop offset=".55" stop-color="#e0ad47"/><stop offset="1" stop-color="#b9812c"/></radialGradient>
<clipPath id="nmPuffClip"><ellipse cx="52" cy="42" rx="34" ry="28"/></clipPath>
<symbol id="nmFishS" viewBox="0 0 60 32">
<path d="M42 16 C48 10 54 4 59 2 C57 9 57 23 59 30 C54 28 48 22 42 16Z" fill="currentColor" fill-opacity=".7"/>
<path d="M44 16 L58 5 M44 16 L58.5 16 M44 16 L58 27" stroke="#000" stroke-opacity=".25" stroke-width=".5" fill="none"/>
<path d="M16 7 C22 0 32 0 38 8 C32 7 24 7 16 7Z" fill="currentColor" fill-opacity=".75"/>
<path d="M22 6 L21 2 M27 6 L27 1.5 M32 6 L33 2.5" stroke="#000" stroke-opacity=".25" stroke-width=".5" fill="none"/>
<path d="M28 24 C32 31 38 31 40 26 C36 26 32 25 28 24Z" fill="currentColor" fill-opacity=".7"/>
<path d="M3 16 C6 6 18 3 28 4 C38 5 44 11 46 16 C44 21 38 27 28 28 C18 29 6 26 3 16Z" fill="currentColor"/>
<path d="M3 16 C6 6 18 3 28 4 C38 5 44 11 46 16 C44 21 38 27 28 28 C18 29 6 26 3 16Z" fill="url(#nmScales)"/>
<path d="M3 16 C6 6 18 3 28 4 C38 5 44 11 46 16 C44 21 38 27 28 28 C18 29 6 26 3 16Z" fill="url(#nmShade)"/>
<ellipse cx="24" cy="9" rx="12" ry="2.2" fill="#fff" fill-opacity=".2"/>
<path d="M13 9 Q16 16 13 23" stroke="#000" stroke-opacity=".3" stroke-width=".8" fill="none"/>
<circle cx="9" cy="13" r="2.7" fill="#f3e9b8"/>
<circle cx="9" cy="13" r="2.7" fill="none" stroke="#000" stroke-opacity=".5" stroke-width=".4"/>
<circle cx="9" cy="13" r="1.6" fill="#0b0b0b"/>
<circle cx="8.4" cy="12.3" r=".55" fill="#fff"/>
<path d="M3.6 17.5 Q5 18.6 6.6 18" stroke="#000" stroke-opacity=".5" stroke-width=".5" fill="none" stroke-linecap="round"/>
</symbol>
<symbol id="nmPuffS" viewBox="0 0 100 80">
<path d="M20 42 C10 36 4 28 5 18 C15 22 24 30 28 38 C24 48 14 56 5 66 C4 56 10 48 20 42Z" fill="#d9a441" fill-opacity=".85" stroke="#8a5d1c" stroke-opacity=".5" stroke-width=".8"/>
<ellipse cx="52" cy="42" rx="34" ry="28" fill="url(#nmPuffBody)"/>
<g clip-path="url(#nmPuffClip)">
<ellipse cx="54" cy="62" rx="30" ry="14" fill="#fbf1cf" fill-opacity=".85"/>
<circle cx="40" cy="30" r="2.4" fill="#6b4416" fill-opacity=".45"/><circle cx="50" cy="24" r="2" fill="#6b4416" fill-opacity=".45"/><circle cx="58" cy="32" r="2.6" fill="#6b4416" fill-opacity=".45"/><circle cx="46" cy="38" r="1.8" fill="#6b4416" fill-opacity=".4"/><circle cx="62" cy="22" r="1.8" fill="#6b4416" fill-opacity=".4"/><circle cx="34" cy="42" r="2" fill="#6b4416" fill-opacity=".4"/>
<rect x="10" y="8" width="90" height="70" fill="url(#nmShade)" fill-opacity=".7"/>
<ellipse cx="50" cy="22" rx="18" ry="5" fill="#fff" fill-opacity=".3"/>
</g>
<ellipse cx="52" cy="42" rx="34" ry="28" fill="none" stroke="#6b4416" stroke-opacity=".45" stroke-width="1"/>
<circle cx="70" cy="49" r="4.2" fill="#ff8a7a" fill-opacity=".4"/>
<circle cx="72" cy="34" r="8.5" fill="#fff"/>
<circle cx="72" cy="34" r="8.5" fill="none" stroke="#3a2a10" stroke-opacity=".6" stroke-width="1.2"/>
<circle cx="74" cy="35" r="5" fill="#111"/>
<circle cx="75.8" cy="32.8" r="1.8" fill="#fff"/><circle cx="72.4" cy="38" r=".9" fill="#fff"/>
<ellipse cx="86" cy="47" rx="3.2" ry="2.6" fill="#7a3b1a"/>
<path d="M54 46 C46 44 42 50 46 57 C52 55 57 51 54 46Z" fill="#e8bf62" stroke="#8a5d1c" stroke-opacity=".5" stroke-width=".8"/>
</symbol>
</defs>
</svg>"""


def get_ocean_background_html(is_diving: bool = False, depth: int = 0) -> str:
    """Generate the full animated sea HTML markup with swimming sea life without leading spaces."""
    darkness = min(0.65, 0.12 + 0.45 * (depth / 200.0)) if is_diving else 0.0

    plankton_pieces = []
    for i in range(18):
        left = f"{(i * 37 + 11) % 97}%"
        top = f"{(i * 53 + 7) % 90}%"
        size = f"{2 + (i % 3)}px"
        dur = f"{3 + (i % 5)}s"
        delay = f"-{i % 4}s"
        plankton_pieces.append(f'<div aria-hidden="true" style="position:absolute;border-radius:50%;background:#A8F0FF;box-shadow:0 0 8px #7FE3EE;left:{left};top:{top};width:{size};height:{size};animation:nmTwinkle {dur} ease-in-out infinite {delay}"></div>')
    plankton_html = "\n".join(plankton_pieces)

    fish_defs = [
        (14, 46, 34, -8, "R", "#2BB7C9", 3.2, 0.7),
        (22, 30, 44, -30, "L", "#5B8DEF", 2.6, 0.6),
        (31, 58, 52, -20, "R", "#FF9A4D", 3.8, 0.5),
        (40, 26, 38, -5, "L", "#5AD1B3", 2.2, 0.7),
        (47, 38, 48, -40, "R", "#FFD166", 3.0, 0.5),
        (74, 50, 56, -15, "L", "#2BB7C9", 3.5, 0.5),
        (82, 28, 36, -22, "R", "#5B8DEF", 2.4, 0.6),
        (66, 34, 42, -33, "L", "#5AD1B3", 2.8, 0.6),
        (28, 18, 40, -12, "R", "#7FE3EE", 1.8, 0.7),
        (29.5, 16, 40, -13, "R", "#7FE3EE", 2.0, 0.7),
        (27, 18, 40, -14, "R", "#7FE3EE", 1.7, 0.7),
    ]
    fishes_pieces = []
    for top, w, dur, delay, direction, color, bob, op in fish_defs:
        anim = f"nmSwimR {dur}s linear infinite {delay}s" if direction == "R" else f"nmSwimL {dur}s linear infinite {delay}s"
        flip = "scaleX(-1)" if direction == "R" else "scaleX(1)"
        fishes_pieces.append(f'<div aria-hidden="true" style="position:absolute;left:0;top:{top}%;width:{w}px;opacity:{op};animation:{anim}"><div style="transform:{flip}"><svg viewBox="0 0 60 32" style="display:block;width:100%;color:{color};animation:nmBob {bob}s ease-in-out infinite"><use href="#nmFishS"/></svg></div></div>')
    fishes_html = "\n".join(fishes_pieces)

    jellies_def = [
        ("30%", "18%", "40px", "#F2A0FF", "9s", "0s"),
        ("80%", "12%", "30px", "#8FB5FF", "11s", "-4s"),
        ("62%", "52%", "46px", "#7FE3EE", "13s", "-7s"),
    ]
    jellies_pieces = []
    for left, top, w, color, dur, delay in jellies_def:
        jellies_pieces.append(f'<div aria-hidden="true" style="position:absolute;opacity:.75;left:{left};top:{top};width:{w};color:{color};filter:drop-shadow(0 0 10px {color});animation:nmJelly {dur} ease-in-out infinite {delay}"><svg viewBox="0 0 40 64" style="display:block;width:100%"><path d="M4 28 C4 6 36 6 36 28 C30 31 26 29 20 31 C14 29 10 31 4 28Z" fill="currentColor" fill-opacity=".5" stroke="currentColor" stroke-width="1.2"/><path d="M4 28 C4 6 36 6 36 28 C30 31 26 29 20 31 C14 29 10 31 4 28Z" fill="url(#nmGloss)" fill-opacity=".6"/><path d="M10 31 C6 42 14 48 9 62 M17 31 C14 42 21 50 16 62 M24 31 C28 42 20 50 25 62 M31 31 C34 42 27 48 31 60" stroke="currentColor" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round" fill="none"/></svg></div>')
    jellies_html = "\n".join(jellies_pieces)

    return f"""{OCEAN_SVG_DEFS}
<div class="nemo-ocean-bg" aria-hidden="true">
<div style="position:absolute;left:-120px;top:80px;width:620px;height:620px;border-radius:50%;background:radial-gradient(circle,rgba(30,90,200,.22),rgba(30,90,200,0) 65%);animation:nmDrift 18s ease-in-out infinite;"></div>
<div style="position:absolute;right:-160px;top:320px;width:680px;height:680px;border-radius:50%;background:radial-gradient(circle,rgba(60,70,210,.2),rgba(60,70,210,0) 65%);animation:nmDrift 23s ease-in-out infinite reverse;"></div>
<div style="position:absolute;left:24%;top:-40px;width:150px;height:560px;transform:rotate(16deg);transform-origin:top;background:linear-gradient(180deg,rgba(150,230,255,.2),rgba(150,230,255,0));filter:blur(10px);animation:nmRay 8s ease-in-out infinite;"></div>
<div style="position:absolute;left:58%;top:-40px;width:120px;height:500px;transform:rotate(12deg);transform-origin:top;background:linear-gradient(180deg,rgba(150,230,255,.16),rgba(150,230,255,0));filter:blur(10px);animation:nmRay 11s ease-in-out infinite 2s;"></div>
{plankton_html}
{fishes_html}
<div style="position:absolute;left:0;top:60%;width:170px;opacity:.85;animation:nmSwimR 95s linear infinite -38s">
<svg viewBox="0 0 120 70" style="display:block;width:100%;animation:nmBob 7s ease-in-out infinite">
<path d="M30 40 C18 46 10 54 8 63 C20 61 30 55 38 46Z" fill="url(#nmSkinG)"/>
<path d="M26 41 C26 12 96 10 100 41Z" fill="url(#nmShellG)"/>
<path d="M42 41 C42 27 51 19 62 16 M62 16 C73 19 82 27 84 41 M62 16 L62 41 M30 36 C36 30 40 28 46 26 M94 36 C88 30 84 28 80 26" stroke="#a9c27a" stroke-opacity=".45" stroke-width="1.6" fill="none"/>
<path d="M34 30 C44 18 64 12 82 16" stroke="#fff" stroke-opacity=".28" stroke-width="3" stroke-linecap="round" fill="none"/>
<path d="M26 41 L100 41 C94 50 32 50 26 41Z" fill="#c9b27a"/>
<path d="M26 41 L100 41 C94 50 32 50 26 41Z" fill="url(#nmShade)"/>
<ellipse cx="108" cy="37" rx="12" ry="8.5" fill="url(#nmSkinG)"/>
<circle cx="112" cy="34" r="2.4" fill="#e6c85a"/>
<circle cx="112.4" cy="34" r="1.3" fill="#111"/>
<path d="M115 40 Q111 43 106 41" stroke="#1d2b1a" stroke-opacity=".7" stroke-width="1.3" stroke-linecap="round" fill="none"/>
<g class="nm-flap"><path d="M80 42 C86 54 100 62 113 62 C107 52 99 46 90 40Z" fill="url(#nmSkinG)" stroke="#2e4a2b" stroke-opacity=".5" stroke-width=".8"/></g>
</svg>
</div>
<div style="position:absolute;left:0;top:36%;width:66px;opacity:.8;animation:nmSwimR 130s linear infinite -60s">
<svg viewBox="0 0 100 80" style="display:block;width:100%;animation:nmBob 5s ease-in-out infinite"><use href="#nmPuffS"/></svg>
</div>
{jellies_html}
<div style="position:absolute;left:0;right:0;bottom:0;height:230px;overflow:hidden">
<svg viewBox="0 0 2880 200" preserveAspectRatio="none" style="position:absolute;left:0;bottom:0;width:200%;height:230px;animation:nmWave 28s linear infinite;opacity:.3">
<path d="M0 100 C360 0 1080 200 1440 100 L1440 200 L0 200Z" fill="#123a7a"/>
<path transform="translate(1440 0)" d="M0 100 C360 0 1080 200 1440 100 L1440 200 L0 200Z" fill="#123a7a"/>
</svg>
<svg viewBox="0 0 2880 200" preserveAspectRatio="none" style="position:absolute;left:0;bottom:0;width:200%;height:160px;animation:nmWave 18s linear infinite;opacity:.4">
<path d="M0 100 C360 0 1080 200 1440 100 L1440 200 L0 200Z" fill="#0a2552"/>
<path transform="translate(1440 0)" d="M0 100 C360 0 1080 200 1440 100 L1440 200 L0 200Z" fill="#0a2552"/>
</svg>
</div>
<svg viewBox="0 0 60 220" style="position:absolute;left:260px;bottom:0;width:52px;height:200px;transform-origin:50% 100%;animation:nmKelp 6s ease-in-out infinite;opacity:.45">
<path d="M30 220 C8 180 52 150 30 110 C8 70 52 40 30 0" stroke="#17725a" stroke-width="9" stroke-linecap="round" fill="none"/>
</svg>
<svg viewBox="0 0 60 220" style="position:absolute;right:8%;bottom:0;width:50px;height:190px;transform-origin:50% 100%;animation:nmKelp 7s ease-in-out infinite .6s;opacity:.45">
<path d="M30 220 C8 180 52 150 30 110 C8 70 52 40 30 0" stroke="#17725a" stroke-width="9" stroke-linecap="round" fill="none"/>
</svg>
<div style="position:absolute;left:28%;bottom:-20px;width:12px;height:12px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 13s linear infinite;"></div>
<div style="position:absolute;left:42%;bottom:-20px;width:8px;height:8px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 10s linear infinite 3s;"></div>
<div style="position:absolute;left:56%;bottom:-20px;width:16px;height:16px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 15s linear infinite 6s;"></div>
<div style="position:absolute;left:70%;bottom:-20px;width:9px;height:9px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 11s linear infinite 1s;"></div>
<div style="position:absolute;left:84%;bottom:-20px;width:14px;height:14px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 14s linear infinite 8s;"></div>
<div style="position:absolute;left:93%;bottom:-20px;width:7px;height:7px;border-radius:50%;border:1px solid rgba(190,240,255,.5);background:rgba(190,240,255,.08);animation:nmRise 9s linear infinite 2s;"></div>
<div style="position:absolute;left:0;top:0;right:0;bottom:0;background:#020819;pointer-events:none;transition:opacity 1.2s ease;opacity:{darkness}"></div>
</div>"""


def render_ocean_background(is_diving: bool = False, depth: int = 0) -> None:
    """Render the animated background HTML via st.markdown."""
    st.markdown(get_ocean_background_html(is_diving=is_diving, depth=depth), unsafe_allow_html=True)
