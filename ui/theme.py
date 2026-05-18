# ══════════════════════════════════════════════════════════════
#  ТЕМА ПРИЛОЖЕНИЯ — ООО ТК «Новочебоксарский»
#  Корпоративный зелёно-графитовый стиль
# ══════════════════════════════════════════════════════════════

# ── Основная палитра ─────────────────────────────────────────
C_BG_DARK    = "#0F1F15"   # очень тёмный фон (боковое меню)
C_BG_MAIN    = "#F4F6F4"   # основной фон страниц
C_BG_CARD    = "#FFFFFF"   # карточки / панели
C_BG_SIDEBAR = "#152A1C"   # боковое меню

C_GREEN_PRIMARY  = "#2D6A4F"  # основной зелёный
C_GREEN_ACCENT   = "#40916C"  # акцентный зелёный (кнопки)
C_GREEN_LIGHT    = "#74C69D"  # светло-зелёный
C_GREEN_ULTRA    = "#B7E4C7"  # очень светлый зелёный (бейджи)

C_GRAPHITE       = "#1B2B22"  # тёмно-графитовый текст
C_TEXT_MAIN      = "#1A2E1F"  # основной текст
C_TEXT_SECONDARY = "#5A7060"  # вторичный текст
C_TEXT_MUTED     = "#8FA896"  # приглушённый текст

C_RED            = "#C0392B"  # ошибка / ниже нормы
C_RED_LIGHT      = "#FDECEA"  # фон предупреждения
C_ORANGE         = "#E67E22"  # предупреждение
C_BLUE           = "#2980B9"  # информация

C_BORDER         = "#D8E8DC"  # граница элементов
C_HOVER          = "#EAF4EE"  # hover-состояние

# ── Шрифты ───────────────────────────────────────────────────
FONT_FAMILY  = "Segoe UI"   # Windows
FONT_TITLE   = (FONT_FAMILY, 20, "bold")
FONT_HEADING = (FONT_FAMILY, 14, "bold")
FONT_BODY    = (FONT_FAMILY, 12)
FONT_SMALL   = (FONT_FAMILY, 10)
FONT_BOLD    = (FONT_FAMILY, 12, "bold")
FONT_NAV     = (FONT_FAMILY, 13)

# ── Размеры ──────────────────────────────────────────────────
SIDEBAR_W    = 230
HEADER_H     = 60
CARD_RADIUS  = 10
BTN_RADIUS   = 8
BTN_H        = 36

# ── Стили кнопок ─────────────────────────────────────────────
BTN_PRIMARY = dict(
    fg_color=C_GREEN_ACCENT,
    hover_color=C_GREEN_PRIMARY,
    text_color="white",
    corner_radius=BTN_RADIUS,
    height=BTN_H,
    font=(FONT_FAMILY, 12, "bold"),
)
BTN_SECONDARY = dict(
    fg_color="transparent",
    hover_color=C_HOVER,
    text_color=C_GREEN_PRIMARY,
    border_color=C_GREEN_ACCENT,
    border_width=1,
    corner_radius=BTN_RADIUS,
    height=BTN_H,
    font=(FONT_FAMILY, 12),
)
BTN_DANGER = dict(
    fg_color=C_RED,
    hover_color="#a93226",
    text_color="white",
    corner_radius=BTN_RADIUS,
    height=BTN_H,
    font=(FONT_FAMILY, 12, "bold"),
)
BTN_NAV = dict(
    fg_color="transparent",
    hover_color="#1F3D28",
    text_color="#B7E4C7",
    anchor="w",
    corner_radius=6,
    height=44,
    font=(FONT_FAMILY, 13),
)
BTN_NAV_ACTIVE = dict(
    fg_color="#2D6A4F",
    hover_color="#2D6A4F",
    text_color="white",
    anchor="w",
    corner_radius=6,
    height=44,
    font=(FONT_FAMILY, 13, "bold"),
)
