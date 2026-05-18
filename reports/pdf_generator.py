"""
PDF-генератор: приходная накладная и акт списания.
Шрифты DejaVu лежат в assets/ рядом с проектом.
"""
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Пути к шрифтам ───────────────────────────────────────────
_BASE   = Path(__file__).parent.parent / "assets"
_FONT_R = _BASE / "DejaVuSans.ttf"
_FONT_B = _BASE / "DejaVuSans-Bold.ttf"

_FN  = "DejaVu"
_FNB = "DejaVu-Bold"

# ── Цвета ────────────────────────────────────────────────────
_GREEN  = colors.HexColor("#2D6A4F")
_GREEN2 = colors.HexColor("#40916C")
_LGRAY  = colors.HexColor("#F4F6F4")
_DGRAY  = colors.HexColor("#1A2E1F")
_RED    = colors.HexColor("#C0392B")
_BORDER = colors.HexColor("#D8E8DC")


def _register():
    try:
        if _FONT_R.exists():
            pdfmetrics.registerFont(TTFont(_FN,  str(_FONT_R)))
        if _FONT_B.exists():
            pdfmetrics.registerFont(TTFont(_FNB, str(_FONT_B)))
    except Exception:
        pass


_register()


def _fn():
    return _FN if _FONT_R.exists() else "Helvetica"


def _fnb():
    return _FNB if _FONT_B.exists() else "Helvetica-Bold"


def _ps(name, size=9, bold=False, align=0, color=colors.black):
    return ParagraphStyle(name,
                          fontName=_fnb() if bold else _fn(),
                          fontSize=size,
                          leading=size + 4,
                          alignment=align,
                          textColor=color)


def _out(prefix, doc_id):
    out = Path(__file__).parent.parent / "reports"
    out.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return out / f"{prefix}_{doc_id}_{ts}.pdf"


def _tbl_style(hdr_color=_GREEN):
    return TableStyle([
        # Заголовок
        ("BACKGROUND",    (0, 0), (-1,  0), hdr_color),
        ("TEXTCOLOR",     (0, 0), (-1,  0), colors.white),
        ("FONTNAME",      (0, 0), (-1,  0), _fnb()),
        ("FONTSIZE",      (0, 0), (-1,  0), 9),
        ("ALIGN",         (0, 0), (-1,  0), "CENTER"),
        # Данные
        ("FONTNAME",      (0, 1), (-1, -1), _fn()),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, _LGRAY]),
        # Сетка
        ("GRID",          (0, 0), (-1, -1), 0.4, _BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])


# ══════════════════════════════════════════════════════════════
#  ПРИХОДНАЯ НАКЛАДНАЯ
# ══════════════════════════════════════════════════════════════
def generate_receipt_pdf(receipt: dict) -> str:
    path = _out("prikhod", receipt["id"])
    doc  = SimpleDocTemplate(
        str(path), pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=2*cm,  rightMargin=2*cm
    )

    dt = (receipt["created_at"].strftime("%d.%m.%Y %H:%M")
          if hasattr(receipt["created_at"], "strftime")
          else str(receipt["created_at"]))
    qty   = int(receipt.get("quantity", 0))
    price = float(receipt.get("price", 0))
    total = qty * price

    els = []

    # ── Шапка ────────────────────────────────────────────────
    header_data = [[
        Paragraph("ООО ТК «Новочебоксарский»<br/>"
                  "<font size=8>д. Кодеркасы, Чебоксарский р-н, Чувашия</font>",
                  _ps("h1", size=10, bold=True)),
        Paragraph(f"ПРИХОДНАЯ НАКЛАДНАЯ<br/>"
                  f"<font size=10>№ {receipt.get('document_number') or receipt['id']}</font>",
                  _ps("h2", size=13, bold=True, align=2, color=_GREEN)),
    ]]
    header_tbl = Table(header_data, colWidths=[10*cm, 7*cm])
    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    els.append(header_tbl)
    els.append(Spacer(1, 0.25*cm))
    els.append(HRFlowable(width="100%", thickness=2.5, color=_GREEN))
    els.append(Spacer(1, 0.3*cm))

    # ── Реквизиты ────────────────────────────────────────────
    req_data = [
        [Paragraph(f"<b>Дата:</b>  {dt}", _ps("r1")),
         Paragraph(f"<b>Поставщик:</b>  {receipt.get('supplier') or '—'}", _ps("r2"))],
        [Paragraph(f"<b>Принял:</b>  {receipt.get('created_by','—')}", _ps("r3")),
         Paragraph("", _ps("r4"))],
    ]
    req_tbl = Table(req_data, colWidths=[8.5*cm, 8.5*cm])
    req_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), _LGRAY),
        ("GRID",       (0,0), (-1,-1), 0.3, _BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    els.append(req_tbl)
    els.append(Spacer(1, 0.4*cm))

    # ── Таблица товаров ──────────────────────────────────────
    tbl_data = [
        ["№", "Наименование материала", "Ед.изм.", "Кол-во", "Цена, руб.", "Сумма, руб."],
        ["1",
         receipt.get("material", ""),
         receipt.get("unit", ""),
         str(qty),
         f"{price:.2f}",
         f"{total:.2f}"],
    ]
    tbl = Table(tbl_data, colWidths=[1*cm, 7.5*cm, 1.8*cm, 2*cm, 2.5*cm, 2.2*cm])
    tbl.setStyle(_tbl_style())
    els.append(tbl)
    els.append(Spacer(1, 0.4*cm))

    # ── Итого ────────────────────────────────────────────────
    итого_data = [[
        Paragraph("", _ps("e")),
        Paragraph(f"ИТОГО:  {total:,.2f} руб.",
                  _ps("tot", size=12, bold=True, align=2, color=_GREEN)),
    ]]
    итого_tbl = Table(итого_data, colWidths=[10*cm, 7*cm])
    итого_tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    els.append(итого_tbl)

    if receipt.get("note"):
        els.append(Spacer(1, 0.2*cm))
        els.append(Paragraph(f"Примечание: {receipt['note']}",
                             _ps("note", size=8, color=colors.grey)))

    # ── Подписи ──────────────────────────────────────────────
    els.append(Spacer(1, 0.5*cm))
    els.append(HRFlowable(width="100%", thickness=0.5, color=_BORDER))
    els.append(Spacer(1, 0.8*cm))
    sign_data = [[
        Paragraph("Сдал: __________________________ / __________________",  _ps("s1")),
        Paragraph("Принял: ________________________ / __________________", _ps("s2")),
    ]]
    sign_tbl = Table(sign_data, colWidths=[8.5*cm, 8.5*cm])
    sign_tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    els.append(sign_tbl)

    doc.build(els)
    return str(path)


# ══════════════════════════════════════════════════════════════
#  АКТ СПИСАНИЯ
# ══════════════════════════════════════════════════════════════
def generate_writeoff_pdf(writeoff: dict) -> str:
    path = _out("spisanie", writeoff["id"])
    doc  = SimpleDocTemplate(
        str(path), pagesize=A4,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        leftMargin=2*cm,  rightMargin=2*cm
    )

    dt = (writeoff["created_at"].strftime("%d.%m.%Y %H:%M")
          if hasattr(writeoff["created_at"], "strftime")
          else str(writeoff["created_at"]))
    qty = int(writeoff.get("quantity", 0))

    els = []

    # ── Шапка ────────────────────────────────────────────────
    header_data = [[
        Paragraph("ООО ТК «Новочебоксарский»<br/>"
                  "<font size=8>д. Кодеркасы, Чебоксарский р-н, Чувашия</font>",
                  _ps("h1", size=10, bold=True)),
        Paragraph(f"АКТ СПИСАНИЯ МАТЕРИАЛОВ<br/>"
                  f"<font size=10>№ {writeoff.get('document_number') or writeoff['id']}</font>",
                  _ps("h2", size=13, bold=True, align=2, color=_RED)),
    ]]
    header_tbl = Table(header_data, colWidths=[10*cm, 7*cm])
    header_tbl.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    els.append(header_tbl)
    els.append(Spacer(1, 0.25*cm))
    els.append(HRFlowable(width="100%", thickness=2.5, color=_RED))
    els.append(Spacer(1, 0.3*cm))

    # ── Реквизиты ────────────────────────────────────────────
    req_data = [
        [Paragraph(f"<b>Дата:</b>  {dt}", _ps("r1")),
         Paragraph(f"<b>Составил:</b>  {writeoff.get('created_by','—')}", _ps("r2"))],
        [Paragraph(f"<b>Основание:</b>  {writeoff.get('reason','—')}", _ps("r3")),
         Paragraph("", _ps("r4"))],
    ]
    req_tbl = Table(req_data, colWidths=[8.5*cm, 8.5*cm])
    req_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), _LGRAY),
        ("GRID",          (0,0),(-1,-1), 0.3, _BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    els.append(req_tbl)
    els.append(Spacer(1, 0.4*cm))

    # ── Таблица ──────────────────────────────────────────────
    tbl_data = [
        ["№", "Наименование материала", "Ед.изм.", "Количество"],
        ["1",
         writeoff.get("material", ""),
         writeoff.get("unit", ""),
         str(qty)],
    ]
    tbl = Table(tbl_data, colWidths=[1*cm, 10.5*cm, 2.5*cm, 3*cm])
    tbl.setStyle(_tbl_style(_RED))
    els.append(tbl)

    if writeoff.get("note"):
        els.append(Spacer(1, 0.3*cm))
        els.append(Paragraph(f"Примечание: {writeoff['note']}",
                             _ps("note", size=8, color=colors.grey)))

    # ── Подписи ──────────────────────────────────────────────
    els.append(Spacer(1, 0.6*cm))
    els.append(HRFlowable(width="100%", thickness=0.5, color=_BORDER))
    els.append(Spacer(1, 0.6*cm))
    els.append(Paragraph("Комиссия:", _ps("cm", bold=True)))
    els.append(Spacer(1, 0.5*cm))

    sign_data = [[
        Paragraph("Председатель: __________________ / ________________", _ps("s1")),
        Paragraph("Член комиссии: _________________ / ________________", _ps("s2")),
    ]]
    sign_tbl = Table(sign_data, colWidths=[8.5*cm, 8.5*cm])
    sign_tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    els.append(sign_tbl)
    els.append(Spacer(1, 0.8*cm))
    els.append(Paragraph(
        "Кладовщик: __________________________ / ________________",
        _ps("s3")))

    doc.build(els)
    return str(path)
