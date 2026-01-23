"""PDF export utilities for copilot responses"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Any, Dict, List


def generate_pdf_report(data: Any, intent: str, title: str = "ERPNext Copilot Report") -> bytes:
    """Generate a PDF report from data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(title, title_style))
    
    # Subtitle with intent and timestamp
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#666'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    story.append(Paragraph(
        f"Query Type: <b>{intent}</b> | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        subtitle_style
    ))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Handle different data types
    if isinstance(data, list):
        story.extend(_render_list_as_table(data, styles))
    elif isinstance(data, dict):
        story.extend(_render_dict_as_section(data, styles))
    else:
        story.append(Paragraph(str(data), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _render_list_as_table(data: List[Dict], styles) -> List:
    """Render list of dictionaries as a table."""
    elements = []
    
    if not data or len(data) == 0:
        elements.append(Paragraph("No data to display.", styles['Normal']))
        return elements
    
    # Get all unique keys
    all_keys = set()
    for item in data:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    columns = sorted(list(all_keys))
    
    # Build table data
    table_data = [columns]  # Header row
    
    for item in data:
        if isinstance(item, dict):
            row = [_format_cell_value(item.get(col, '')) for col in columns]
            table_data.append(row)
        else:
            table_data.append([str(item)])
    
    # Create table
    table = Table(table_data, colWidths=[7.5*inch / len(columns)] * len(columns))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    
    elements.append(table)
    return elements


def _render_dict_as_section(data: Dict, styles) -> List:
    """Render dictionary as formatted sections."""
    elements = []
    
    for key, value in data.items():
        # Section title
        title = Paragraph(f"<b>{key}</b>", styles['Heading3'])
        elements.append(title)
        
        # Section content
        if isinstance(value, dict):
            for k, v in value.items():
                para = Paragraph(f"<b>{k}:</b> {_format_cell_value(v)}", styles['Normal'])
                elements.append(para)
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                # Render as table
                elements.extend(_render_list_as_table(value, styles))
            else:
                # Render as bullet points
                for item in value:
                    para = Paragraph(f"• {_format_cell_value(item)}", styles['Normal'])
                    elements.append(para)
        else:
            para = Paragraph(_format_cell_value(value), styles['Normal'])
            elements.append(para)
        
        elements.append(Spacer(1, 0.2*inch))
    
    return elements


def _format_cell_value(value: Any) -> str:
    """Format a value for display in PDF."""
    if value is None:
        return "—"
    elif isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        return ", ".join([str(v) for v in value[:5]]) + ("..." if len(value) > 5 else "")
    elif isinstance(value, dict):
        return str(value)
    else:
        return str(value)[:100]  # Truncate long strings


def add_anomaly_section(data: Dict, styles) -> List:
    """Special rendering for price anomaly data."""
    elements = []
    
    if 'anomalies' in data:
        elements.append(Paragraph("<b>Price Anomalies Detected</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.15*inch))
        
        anomalies = data['anomalies']
        if anomalies:
            # Table for anomalies
            table_data = [['Item', 'Supplier', 'Price', 'Avg Price', 'Difference', 'Severity']]
            for anomaly in anomalies[:20]:  # Limit to 20 rows per page
                table_data.append([
                    anomaly.get('item_name', ''),
                    anomaly.get('supplier', ''),
                    anomaly.get('price', ''),
                    anomaly.get('average_price', ''),
                    anomaly.get('difference', ''),
                    anomaly.get('severity', ''),
                ])
            
            table = Table(table_data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f44')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff0f0')]),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No price anomalies detected.", styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
    
    if 'summary' in data:
        elements.append(Paragraph("<b>Summary</b>", styles['Heading3']))
        summary = data['summary']
        for key, value in summary.items():
            para = Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", styles['Normal'])
            elements.append(para)
        elements.append(Spacer(1, 0.2*inch))
    
    if 'recommendations' in data:
        elements.append(Paragraph("<b>Recommendations</b>", styles['Heading3']))
        for rec in data['recommendations'][:5]:  # Limit to 5 recommendations
            para = Paragraph(f"• {rec}", styles['Normal'])
            elements.append(para)
    
    return elements
