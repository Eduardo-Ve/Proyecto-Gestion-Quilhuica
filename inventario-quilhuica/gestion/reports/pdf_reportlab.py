from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from django.conf import settings
from datetime import datetime
import os
import io
import re


def generar_pdf_reportlab(report_type, data, start, end):
    """Genera un PDF institucional con márgenes y ancho total ajustado."""
    buffer = io.BytesIO()
    pagesize = landscape(A4)

    # Márgenes cómodos con buen espacio en los bordes
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title=f"Reporte {report_type.capitalize()} - Gestión Quilhuica",
    )

    story = []
    styles = getSampleStyleSheet()

    # === ENCABEZADO ===
    logo_path = os.path.join(settings.BASE_DIR, "reports", "static", "img", "logo.png")
    if not os.path.exists(logo_path):
        logo_path = None

    header_text = Paragraph(
        "<b>Gestión Quilhuica</b><br/>Quilhuica SPA<br/>"
        f"{datetime.now().strftime('%d/%m/%Y')}",
        ParagraphStyle("headerLeft", fontSize=9, leading=12, alignment=TA_LEFT),
    )
    logo = Image(logo_path, width=2.4 * cm, height=2.4 * cm) if logo_path else ""
    header_table = [[header_text, logo]]
    header = Table(header_table, colWidths=[17 * cm, 3 * cm])
    header.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header)
    story.append(Spacer(1, 0.4 * cm))

    # === TÍTULO ===
    title = Paragraph(
        f"<b>Reporte de {report_type.capitalize()}</b>",
        ParagraphStyle("title", fontSize=14, leading=17, alignment=TA_CENTER, spaceAfter=8),
    )
    story.append(title)
    story.append(Spacer(1, 0.3 * cm))

    # === TABLA ===
    if data:
        table = _build_table(data, report_type)
        table.hAlign = "LEFT"  # Alinear tabla a la izquierda
        story.append(table)
    else:
        story.append(Paragraph("No hay datos para mostrar.", styles["Normal"]))

    # === FOOTER ===
    footer_text = (
        f"<font size='8'>Sistema Gestión Quilhuica ERP — Generado el "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
        "© Quilhuica SPA | Uso interno</font>"
    )
    footer = Paragraph(
        footer_text,
        ParagraphStyle("footer", fontSize=8, leading=10, alignment=TA_LEFT),
    )
    story.append(Spacer(1, 0.55 * cm))
    story.append(footer)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


# ===============================================================
# TABLA
# ===============================================================
def _build_table(data, report_type):
    headers = _normalize_headers(list(data[0].keys()))
    rows = []

    for item in data:
        row = []
        for key, value in item.items():
            if "Descripción" in key or "descripción" in key.lower():
                # Columna de descripción con ajuste automático (wrap text como Excel)
                cell = Paragraph(
                    str(value),
                    ParagraphStyle(
                        "desc",
                        fontSize=8,
                        leading=10,
                        alignment=TA_LEFT,
                        wordWrap="LTR",
                        splitLongWords=True,  # Divide palabras largas
                        breakLongWords=True,  # Rompe palabras si es necesario
                    ),
                )
                row.append(cell)
            else:
                row.append(str(value))
        rows.append(row)

    rows.insert(0, headers)
    
    # Configurar colWidths ANTES de crear la tabla para que Paragraph calcule correctamente
    col_widths = _get_column_widths(headers, report_type)
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    # === ESTILO GENERAL ===
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#00C853")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),  # Tamaño uniforme en headers
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),  # Padding consistente
                ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("VALIGN", (0, 1), (-1, -1), "TOP"),
                ("ALIGN", (0, 1), (-2, -1), "CENTER"),
                ("ALIGN", (-1, 1), (-1, -1), "LEFT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]
        )
    )

    return table


# ===============================================================
# CABECERAS
# ===============================================================
def _normalize_headers(headers):
    fixed = []
    for h in headers:
        h = re.sub(r"[_\-]+", " ", h)
        h = h.strip().capitalize()
        fixed.append(h)
    return fixed


# ===============================================================
# ANCHOS POR TIPO DE REPORTE
# ===============================================================
def _get_column_widths(headers, report_type):
    """Ajusta proporciones para usar el ancho disponible con márgenes cómodos."""
    # Ancho útil: landscape A4 (29.7 cm) - márgenes (2.5*2 = 5.0 cm) = ~24.7 cm disponible
    col_widths = []

    if report_type == "movimientos":
        # Anchos optimizados - descripción ajustada con espacio para márgenes
        for h in headers:
            if "Descripción" in h or "descripción" in h.lower():
                col_widths.append(5.0 * cm)  # Reducida para dejar espacio a los lados
            elif "Fecha" in h:
                col_widths.append(3.3 * cm)
            elif "Usuario" in h:
                col_widths.append(2.0 * cm)
            elif "Cantidad" in h:
                col_widths.append(2.0 * cm)
            elif "Origen" in h or "Destino" in h:
                col_widths.append(2.6 * cm)
            elif "Presentación" in h or "Producto" in h:
                col_widths.append(2.8 * cm)
            elif "Tipo" in h:
                col_widths.append(2.0 * cm)
            elif "ID" in h or "Id" in h:
                col_widths.append(1.1 * cm)
            else:
                col_widths.append(1.6 * cm)

    elif report_type == "inventario":
        # Igualar ancho total visual al de movimientos (~24.5 cm)
        # Se mantiene proporción pero se ensanchan ligeramente las columnas
        for h in headers:
            if "Bodega" in h:
                col_widths.append(4.0 * cm)
            elif "Producto" in h:
                col_widths.append(4.0 * cm)
            elif "Presentación" in h or "Presentacion" in h:
                col_widths.append(4.0 * cm)
            elif "Cantidad" in h and "paquetes" in h.lower():
                col_widths.append(3.5 * cm)
            elif "Total" in h and "contenido" in h.lower():
                col_widths.append(3.5 * cm)
            elif "Actualización" in h or "Ultima" in h or "actualizacion" in h.lower():
                col_widths.append(5.5 * cm)  # más espacio para alinear bien
            else:
                col_widths.append(3.0 * cm)

        # Normalizar si supera el ancho total útil (24.5 cm)
        total_width = sum(col_widths)
        if total_width > 24.5 * cm:
            scale_factor = (24.5 * cm) / total_width
            col_widths = [w * scale_factor for w in col_widths]

    elif report_type == "aplicaciones":
        # Ajuste para igualar el tamaño con inventario (~24.5 cm)
        for h in headers:
            if "ID" in h or "Id" in h or "aplicacion" in h.lower():
                col_widths.append(3.0 * cm)
            elif "Fecha" in h:
                col_widths.append(4.0 * cm)
            elif "Caseta" in h:
                col_widths.append(4.5 * cm)
            elif "Producto" in h:
                col_widths.append(4.5 * cm)
            elif "Cantidad" in h:
                col_widths.append(4.0 * cm)
            elif "Usuario" in h:
                col_widths.append(4.5 * cm)
            else:
                col_widths.append(3.0 * cm)

        # Normalizar si excede ancho útil
        total_width = sum(col_widths)
        if total_width > 24.5 * cm:
            scale_factor = (24.5 * cm) / total_width
            col_widths = [w * scale_factor for w in col_widths]
        # Verificar que no exceda el ancho disponible (suma debe ser <= 24.5 cm)
        total_width = sum(col_widths)
        if total_width > 24.5 * cm:
            # Escalar proporcionalmente si excede
            scale_factor = (24.5 * cm) / total_width
            col_widths = [w * scale_factor for w in col_widths]
    
    else:
        col_widths = [3 * cm] * len(headers)

    return col_widths