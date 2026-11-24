#!/usr/bin/env python3
"""Build high-converting Korean Digital Excel Storefront (https://0520goeus.github.io/excel-store/) with crisp preview images."""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "https://0520goeus.github.io/excel-store"
CHECKOUT_URL = "https://scopekit-studio.lemonsqueezy.com/checkout/buy/ba4f11c6-8609-49c0-a947-39bead163d74"
INDEXNOW_KEY = "f3b89c14e72a41d8a609c5e2b713d481"
ADSENSE_CLIENT = "ca-pub-8749404731911210"
GSC_FILE = "google873809343766a3b6.html"
GSC_CONTENT = "google-site-verification: google873809343766a3b6.html"
TODAY = datetime.now().strftime("%Y-%m-%d")

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
IMG_DIR = DIST / "img"


def _font(size: int, bold: bool = True):
    for p in (
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size, index=7 if bold and p.endswith(".ttc") else 0)
            except Exception:
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    return ImageFont.load_default()


def render_sheet_preview(out_path: Path, banner_title: str, banner_color: tuple[int, int, int], headers: list[str], rows: list[list[str]], highlight_col: int | None = None) -> None:
    """Render a realistic crisp Excel sheet screenshot preview PNG (works on macOS & Linux CI)."""
    W, H = 1040, 560
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # Excel top window chrome
    d.rectangle([0, 0, W, 42], fill=(21, 128, 61))
    d.text((18, 11), f"Excel  |  {banner_title}", font=_font(18, True), fill=(255, 255, 255))

    # Formula bar
    d.rectangle([0, 42, W, 76], fill=(241, 245, 249))
    d.line([(0, 76), (W, 76)], fill=(203, 213, 225), width=1)
    d.text((18, 51), "fx   =IF(C4>0, ROUND(C4-D4-(C4*E4/100)-F4-G4, 0), 0)   |   노란색 입력칸만 수정 → 전체 자동 계산", font=_font(14, False), fill=(51, 65, 85))

    # Sheet title row
    d.rectangle([24, 92, W - 24, 140], fill=banner_color)
    d.text((40, 104), banner_title, font=_font(22, True), fill=(255, 255, 255))

    # Table grid
    cols = len(headers)
    table_w = W - 48
    col_w = table_w // cols
    y = 152
    row_h = 48

    # Header row
    for i, h in enumerate(headers):
        x0 = 24 + i * col_w
        x1 = x0 + col_w
        d.rectangle([x0, y, x1, y + row_h], fill=(30, 41, 59), outline=(203, 213, 225), width=1)
        d.text((x0 + 10, y + 14), h, font=_font(15, True), fill=(255, 255, 255))
    y += row_h

    # Data rows
    for r_idx, r in enumerate(rows):
        for i, val in enumerate(r):
            x0 = 24 + i * col_w
            x1 = x0 + col_w
            bg = (254, 249, 195) if i in (1, 2) else ((248, 250, 252) if r_idx % 2 else (255, 255, 255))
            fg = (15, 23, 42)
            if highlight_col is not None and i == highlight_col:
                if "적자" in val or "월세" in val:
                    bg, fg = (254, 226, 226), (185, 28, 28)
                elif "흑자" in val or "유리" in val or "%" in val:
                    bg, fg = (220, 252, 231), (21, 128, 61)
            d.rectangle([x0, y, x1, y + row_h], fill=bg, outline=(203, 213, 225), width=1)
            d.text((x0 + 10, y + 14), val, font=_font(15, i == highlight_col or i == 0), fill=fg)
        y += row_h

    # Footer badge
    d.rounded_rectangle([24, H - 56, W - 24, H - 16], radius=10, fill=(241, 245, 249))
    d.text((40, H - 45), "노란색 셀: 사용자 입력   |   흰색·초록·빨강 셀: 자동 수식(SUMIF · PMT · IF · 조건부 서식)   |   매크로 0%", font=_font(15, True), fill=(30, 41, 59))
    img.save(out_path, "PNG")


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Render crisp previews only if local font available (or always render — Pillow works on CI too)
    render_sheet_preview(
        IMG_DIR / "preview_seller.png",
        "1인 셀러 스마트스토어·쿠팡 마진·ROAS·부가세 자동정산 v2",
        (15, 23, 42),
        ["상품명", "판매가", "원가", "수수료·배송", "부가세", "손익분기ROAS", "판정"],
        [
            ["무선 선풍기", "29,900원", "12,500원", "4,783원", "1,582원", "271%", "흑자운영"],
            ["주방 매트", "19,800원", "6,800원", "5,338원", "1,182원", "306%", "적자경보"],
            ["고속 충전기", "24,900원", "8,200원", "7,089원", "1,518원", "308%", "흑자운영"],
            ["캠핑 의자", "45,000원", "21,000원", "6,034원", "2,182원", "285%", "흑자운영"],
        ],
        highlight_col=6,
    )
    render_sheet_preview(
        IMG_DIR / "preview_house.png",
        "2026 내집마련 매물 10개 비교 · 대출 PMT·취득세·복비 자동계산",
        (29, 78, 216),
        ["후보 매물", "매매가", "대출금", "월 원리금", "취득세", "복비상한", "필요현금"],
        [
            ["A단지 84㎡", "6.5억", "3.5억(4.1%)", "1,691,194원", "910만원", "286만원", "3억 1,196만"],
            ["B단지 59㎡", "5.2억", "3.0억(3.9%)", "1,415,005원", "572만원", "229만원", "2억 2,801만"],
            ["C단지 84㎡", "8.2억", "4.5억(4.3%)", "2,226,923원", "2,225만원", "361만원", "3억 9,586만"],
            ["전세vs월세", "전세 4.2억", "월세 1.5억/95", "전환율 4.22%", "이자 85.5만", "차액 +9.5만", "전세대출 유리"],
        ],
        highlight_col=6,
    )
    render_sheet_preview(
        IMG_DIR / "preview_budget.png",
        "2026 월급 가계부 · 고정비 · 순자산 자동 대시보드 v1",
        (15, 118, 110),
        ["구분 항목", "월 예산", "실제 합계", "예산 차액", "수입 대비", "연간 예상"],
        [
            ["월 실수령 수입", "3,500,000", "3,500,000", "0원", "100.0%", "42,000,000"],
            ["고정 지출 합계", "1,300,000", "1,010,000", "+290,000", "28.9%", "12,120,000"],
            ["변동 지출 합계", "900,000", "645,000", "+255,000", "18.4%", "7,740,000"],
            ["월 순저축액", "1,300,000", "1,845,000", "+545,000", "52.7% 달성", "22,140,000"],
        ],
        highlight_col=4,
    )

    ld_product = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "2026 직장인·1인셀러 무매크로 자동계산 엑셀 3종 올인원 번들",
        "image": f"{BASE_URL}/img/preview_seller.png",
        "description": "1인셀러 마진·ROAS·부가세 정산 v2 + 내집마련 매물 10개 대출·취득세·복비 비교 + 월급 가계부·순자산 대시보드 무매크로 엑셀 3종 패키지.",
        "offers": {
            "@type": "Offer",
            "url": CHECKOUT_URL,
            "priceCurrency": "USD",
            "price": "19.00",
            "availability": "https://schema.org/InStock",
        },
    }

    page_html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>2026 직장인·1인셀러 무매크로 자동계산 엑셀 3종 올인원 번들 — 즉시 다운로드</title>
<meta name="description" content="노란 칸만 입력하면 1초 자동 계산! 스마트스토어·쿠팡 마진·ROAS 적자경보 + 내집마련 매물 10개 대출·취득세·복비 비교 + 월급 가계부·순자산 대시보드 3종 올인원 번들.">
<link rel="canonical" href="{BASE_URL}/">
<meta property="og:type" content="product">
<meta property="og:title" content="2026 직장인·1인셀러 무매크로 자동계산 엑셀 3종 올인원 번들">
<meta property="og:description" content="개별 가치 48,700원 → 올인원 번들 $19 (약 26,000원). 결제 후 3초 즉시 ZIP 다운로드, 매크로 0%, 맥/윈도우/구글시트 100% 호환.">
<meta property="og:image" content="{BASE_URL}/img/preview_seller.png">
<meta name="google-site-verification" content="E0MKLI_9g0wTNR9pjNKmxb_QGiA51AIK93dV9qBKumg">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
<script type="application/ld+json">{json.dumps(ld_product, ensure_ascii=False)}</script>
<style>
:root{{--bg:#0b1120;--card:#111827;--panel:#1e293b;--ink:#f8fafc;--muted:#94a3b8;--accent:#facc15;--teal:#14b8a6;--line:#334155;}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;background:var(--bg);color:var(--ink);line-height:1.7}}
.wrap{{max-width:980px;margin:0 auto;padding:0 18px}}
.hero{{padding:54px 0 40px;text-align:center;background:radial-gradient(circle at top,#1e3a8a 0%,#0b1120 65%)}}
.badge{{display:inline-block;background:rgba(20,184,166,.18);border:1px solid var(--teal);color:#5eead4;padding:5px 14px;border-radius:999px;font-size:13px;font-weight:700;margin-bottom:14px}}
h1{{margin:0 0 14px;font-size:clamp(26px,4.5vw,42px);line-height:1.25}}
.lead{{max-width:680px;margin:0 auto 26px;color:#cbd5e1;font-size:16px}}
.price-box{{display:inline-flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:14px;background:var(--panel);border:1px solid var(--line);padding:16px 24px;border-radius:16px;margin-bottom:22px}}
.strike{{text-decoration:line-through;color:var(--muted);font-size:16px}}
.now{{font-size:32px;font-weight:900;color:var(--accent)}}
.cta-btn{{display:inline-block;background:var(--accent);color:#0f172a;font-weight:900;font-size:18px;padding:16px 34px;border-radius:14px;text-decoration:none;box-shadow:0 10px 28px rgba(250,204,21,.28);transition:.15s}}
.cta-btn:hover{{transform:translateY(-2px);filter:brightness(1.05)}}
.sub-note{{font-size:13px;color:var(--muted);margin-top:12px}}
section{{padding:34px 0}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:24px;margin-bottom:22px}}
.card h2{{margin:0 0 8px;font-size:22px;color:#fff}}
.card p{{color:#cbd5e1;margin:0 0 14px}}
.preview{{width:100%;border-radius:12px;border:1px solid var(--line);display:block;margin-top:12px}}
.grid3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin-top:14px}}
.mini{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}}
.mini h3{{margin:0 0 6px;font-size:16px;color:#5eead4}}
.calc{{background:var(--panel);border-radius:14px;padding:18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;align-items:end}}
label{{font-size:12px;color:#cbd5e1;display:block}}
input{{width:100%;margin-top:4px;padding:9px 10px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;font-size:15px}}
.calc-out{{grid-column:1/-1;background:#0f172a;border-left:4px solid var(--teal);padding:12px 14px;border-radius:8px;font-size:15px}}
table{{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px}}
th,td{{padding:11px 12px;border:1px solid var(--line);text-align:left}}
th{{background:var(--panel);color:#fff}}
.sticky{{position:sticky;bottom:14px;z-index:20;max-width:740px;margin:20px auto 0;background:rgba(15,23,42,.95);backdrop-filter:blur(8px);border:1px solid var(--teal);border-radius:14px;padding:12px 18px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px}}
footer{{border-top:1px solid var(--line);padding:28px 0 60px;color:var(--muted);font-size:13px;text-align:center}}
footer a{{color:#93c5fd;text-decoration:none;margin:0 6px}}
</style>
</head>
<body>
<header class="hero">
  <div class="wrap">
    <div class="badge">2026 최신판 · VBA 매크로 0% · 평생소장 즉시 다운로드</div>
    <h1>노란 칸만 입력하면 1초 완성!<br>직장인·1인셀러 자동계산 엑셀 3종 올인원</h1>
    <p class="lead">스마트스토어·쿠팡 팔수록 적자나는 상품 자동 차단부터, 내집마련 매물 10개 대출·취득세·복비 비교, 월급 가계부·순자산 대시보드까지 — 실무 수식이 완성된 3개 워크북을 한 번에 소장하세요.</p>
    <div class="price-box">
      <span class="strike">개별 정가 합계 ₩48,700</span>
      <span class="now">$19 <span style="font-size:15px;font-weight:600;color:#cbd5e1">(약 ₩26,000 · 46% 할인)</span></span>
    </div><br>
    <a class="cta-btn" href="{CHECKOUT_URL}" target="_blank" rel="noopener">지금 바로 3종 번들 다운로드 ($19) →</a>
    <div class="sub-note">신용/체크카드 · Apple Pay · PayPal 지원 · 결제 직후 3초 내 ZIP 파일 즉시 다운로드 · Windows Excel / Mac Numbers / Google Sheets 호환</div>
  </div>
</header>

<main class="wrap">
  <section>
    <div class="card">
      <h2>⚡ 3초 미리 체험: 내 상품 손익분기 ROAS 계산기</h2>
      <p>엑셀 파일에 내장된 공식과 동일한 로직을 지금 바로 테스트해 보세요. (엑셀에서는 수십 개 SKU를 한 번에 자동 판정 + 적자 빨간불 표시!)</p>
      <div class="calc">
        <label>판매가 (원)<input id="sp" type="number" value="29900" oninput="runDemo()"></label>
        <label>매입원가 (원)<input id="co" type="number" value="12500" oninput="runDemo()"></label>
        <label>마켓수수료 (%)<input id="fe" type="number" step="0.1" value="5.63" oninput="runDemo()"></label>
        <label>택배·포장비 (원)<input id="sh" type="number" value="3100" oninput="runDemo()"></label>
        <div class="calc-out" id="demoOut"></div>
      </div>
    </div>

    <div class="card">
      <h2>01. 1인 셀러 통합 마진·ROAS·부가세 정산 v2 (단품가 ₩19,900)</h2>
      <p>스마트스토어·쿠팡·로켓그로스 수수료와 부가세 `(판매가-매입가)÷11`을 자동 차감하고, 현재 ROAS가 손익분기 ROAS보다 낮으면 빨간색 <strong>적자경보</strong>가 자동 점등됩니다. 월별 부가세·종소세 예비비 시트 포함.</p>
      <img class="preview" src="img/preview_seller.png" alt="1인 셀러 마진 ROAS 자동정산 엑셀 미리보기">
    </div>

    <div class="card">
      <h2>02. 내집마련 매물 10개 비교 · 대출·전월세·복비 자동 시트 v1 (단품가 ₩15,900)</h2>
      <p>임장 다녀온 후보 매물 최대 10개를 한 표에 넣으면 `PMT` 월 원리금, 2026 1주택 취득세(6억~9억 구간 포함), 생애최초 200만원 감면, 복비 상한, 총 필요 자기자본과 전세 vs 월세 손익분기까지 1초 만에 비교합니다.</p>
      <img class="preview" src="img/preview_house.png" alt="내집마련 매물 10개 비교 대출 취득세 복비 엑셀 미리보기">
    </div>

    <div class="card">
      <h2>03. 월급 가계부 · 고정비 · 순자산 자동 대시보드 v1 (단품가 ₩12,900)</h2>
      <p>수입·고정지출·변동지출 입력만으로 `SUMIF` 자동 집계, 저축률, 연간 누적 예상 저축액, 자산-부채 순자산 트래커까지 한눈에 파악할 수 있습니다.</p>
      <img class="preview" src="img/preview_budget.png" alt="월급 가계부 순자산 자동 대시보드 엑셀 미리보기">
    </div>

    <div class="card">
      <h2>왜 이 3종 번들이 압도적으로 편한가요?</h2>
      <div class="grid3">
        <div class="mini"><h3>보안 경고 0% (무매크로)</h3><p>위험한 VBA 매크로 대신 표준 엑셀 함수만 사용해 회사 PC·맥북·구글 시트 어디서나 오류 없이 열립니다.</p></div>
        <div class="mini"><h3>결제 후 3초 즉시 전달</h3><p>판매자 연락을 기다릴 필요 없이 결제 완료 화면과 이메일로 3종 `.xlsx` + 사용설명서 ZIP이 즉시 전달됩니다.</p></div>
        <div class="mini"><h3>무료 웹 계산기 11종 연동</h3><p>모바일에서도 바로 쓸 수 있는 부동산·자동차·연봉·셀러 무료 계산기 11종을 평생 함께 이용하실 수 있습니다.</p></div>
      </div>
      <table>
        <thead><tr><th>포함 파일</th><th>핵심 자동화 수식</th><th>개별 가치</th></tr></thead>
        <tbody>
          <tr><td>2026_1인셀러_통합_마진_ROAS_부가세_정산_v2.xlsx</td><td>부가세·마진율·손익분기ROAS·적자경보 조건부서식</td><td>₩19,900</td></tr>
          <tr><td>2026_내집마련_대출_전월세_복비_비교시트_v1.xlsx</td><td>PMT 원리금·1주택/생애최초 취득세·복비·전월세 판정</td><td>₩15,900</td></tr>
          <tr><td>2026_월급_가계부_자산관리_자동대시보드_v1.xlsx</td><td>SUMIF 자동집계·저축률·연간예상·순자산 트래커</td><td>₩12,900</td></tr>
          <tr><td>사용설명서_README.txt + 무료 웹 계산기 링크</td><td>1분 빠른 시작 가이드</td><td>무료 포함</td></tr>
          <tr><td><strong>3종 올인원 번들 최종가</strong></td><td><strong>1회 결제 평생 소장 (구독료 없음)</strong></td><td><strong style="color:#facc15">$19 (약 ₩26,000)</strong></td></tr>
        </tbody>
      </table>
    </div>

    <div class="card">
      <h2>자주 묻는 질문 (FAQ)</h2>
      <p><strong>Q. 엑셀이 없어도 사용할 수 있나요?</strong><br>A. 네! 무료 구글 시트(Google Sheets)에 파일을 올리거나 맥 기본 앱인 Numbers에서 열어도 모든 수식이 정상 작동합니다.</p>
      <p><strong>Q. 국내 체크카드/신용카드로도 결제되나요?</strong><br>A. 네! 해외결제(Visa/Master/AMEX)가 가능한 국내 신용·체크카드, Apple Pay, PayPal로 10초 만에 결제되며 즉시 다운로드 링크가 열립니다.</p>
      <p><strong>Q. 결제 후 파일은 어디서 받나요?</strong><br>A. 결제 완료 즉시 화면에 다운로드 버튼이 나타나며, 입력하신 이메일로도 영구 다운로드 링크가 자동 발송됩니다.</p>
    </div>

    <div class="sticky">
      <div><strong>2026 무매크로 자동 엑셀 3종 올인원</strong> <span style="color:#facc15;font-weight:800;margin-left:8px">$19</span></div>
      <a class="cta-btn" style="padding:10px 20px;font-size:15px" href="{CHECKOUT_URL}" target="_blank" rel="noopener">즉시 다운로드 받기 →</a>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <div style="margin-bottom:10px">
      <a href="https://0520goeus.github.io/house-calc-kr/">부동산·대출 계산기</a>
      <a href="https://0520goeus.github.io/car-calc-kr/">자동차세·유지비</a>
      <a href="https://0520goeus.github.io/money-calc-kr/">실수령액·금융</a>
      <a href="https://0520goeus.github.io/benefit-calc-kr/">2026 지원금</a>
      <a href="https://0520goeus.github.io/seller-margin-calc/">셀러 마진 계산기</a>
      <a href="https://0520goeus.github.io/elec-calc/">전기세 얼마</a>
      <a href="https://0520goeus.github.io/vs-pick/">가성비 VS 124종</a>
    </div>
    <div>© 2026 해뎐 디지털 템플릿 스토어 · Updated {TODAY}</div>
  </div>
</footer>
<script>
function runDemo(){{
  const sp=+document.getElementById('sp').value||0;
  const co=+document.getElementById('co').value||0;
  const fe=+document.getElementById('fe').value||0;
  const sh=+document.getElementById('sh').value||0;
  const vat=Math.max(0, Math.round((sp-co)/11));
  const profit=Math.round(sp-co-(sp*fe/100)-sh-vat);
  const margin=sp>0?(profit/sp):0;
  const roas=margin>0?Math.round(100/margin):0;
  document.getElementById('demoOut').innerHTML =
    `광고 전 순이익: <strong>${{profit.toLocaleString()}}원</strong> (마진율 <strong>${{(margin*100).toFixed(1)}}%</strong> · 부가세 ${{vat.toLocaleString()}}원) → 손익분기 ROAS: <strong style="color:#facc15">${{roas}}%</strong> (${{roas}}% 미만 광고는 적자!)`;
}}
runDemo();
</script>
</body>
</html>"""

    (DIST / "index.html").write_text(page_html, encoding="utf-8")
    (DIST / "ads.txt").write_text(f"google.com, {ADSENSE_CLIENT.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (DIST / GSC_FILE).write_text(GSC_CONTENT, encoding="utf-8")
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{BASE_URL}/</loc><lastmod>{TODAY}</lastmod></url>\n</urlset>\n',
        encoding="utf-8",
    )
    print(f"Built excel-store -> {DIST}")


if __name__ == "__main__":
    main()
