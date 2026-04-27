from app.core.time_utils import get_bahia_time_str
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def gerar_pdf_cotacao_logistica(dados_previa):
    """
    Constrói o arquivo PDF de Cotação Logística usando ReportLab.
    
    Estrutura do PDF:
    - Título e Logo.
    - Justificativa Técnica (Texto fixo).
    - Resumo (Total de pessoas, Custo Total, Data).
    - Tabela de Eventos (Discriminação por grupo/evento com custos de alimentação e equipe).
    - Valor por Extenso.
    - Espaço para Assinatura.
    
    Args:
        dados_previa (dict): Dicionário retornado por 'calculate_logistics_preview'.
        
    Returns:
        BytesIO: Buffer contendo o PDF gerado.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'TitleCustom', 
        parent=styles['Heading1'], 
        alignment=1, 
        spaceAfter=20
    )
    story.append(Paragraph("COTAÇÃO OFICIAL - LOGÍSTICA ABARÉ", title_style))
    # Logo
    import os
    from reportlab.platypus import Image
    logo_path = "app/static/imagens/logo-agendha.jpg"
    if os.path.exists(logo_path):
        im = Image(logo_path, width=100, height=50) # Aspect ratio approx 2:1
        im.hAlign = 'CENTER'
        story.append(im)
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 12))

    
    # Justificativa Técnica
    justificativa = """
    A cotação baseia-se no acolhimento dos beneficiários para o treinamento técnico, 
    garantindo alimentação (Café e Almoço) durante os 02 dias de atividades, 
    além das diárias da equipe técnica necessária.
    """
    story.append(Paragraph(justificativa, styles['Italic']))
    story.append(Spacer(1, 15))

    # Summary Info
    info_text = f"""
    <b>Total Beneficiários:</b> {dados_previa['total_candidatos']}<br/>
    <b>Custo Total Estimado:</b> R$ {dados_previa['custo_total_estimado']:.2f}<br/>
    <b>Data:</b> {get_bahia_time_str()}
    """
    story.append(Paragraph(info_text, styles['Normal']))
    story.append(Spacer(1, 20))

    # Events Table
    data = [['Evento', 'Qtd. Pessoas', 'Alimentação', 'Equipe/Diárias', 'Total']]
    
    for grupo in dados_previa['grupos']:
        data.append([
            grupo['nome_evento'],
            str(grupo['quantidade_beneficiarios']),
            f"R$ {grupo['detalhes_custo']['kits']:.2f}",
            f"R$ {grupo['detalhes_custo']['logistica']:.2f}",
            f"R$ {grupo['custo_estimado']:.2f}"
        ])
    
    # Add Grand Total Row
    total_val = dados_previa['custo_total_estimado']
    data.append(['TOTAL GERAL', '', '', '', f"R$ {total_val:.2f}"])

    table = Table(data, colWidths=[150, 80, 80, 90, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), # Macururé Style (Dark Blue?)
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Total row bold
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Valor por Extenso (Simple Implementation inline or placeholder if lib missing)
    # Assuming we want a visual representation.
    try:
        from num2words import num2words
        extenso = num2words(total_val, lang='pt_BR', to='currency')
    except ImportError:
        extenso = f"Valor numérico de R$ {total_val:.2f}"

    story.append(Paragraph(f"<b>Valor Total:</b> {extenso.capitalize()}", styles['Normal']))
    story.append(Spacer(1, 30))

    # Signature
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        alignment=1, # Center
        spaceBefore=30
    )
    
    story.append(Paragraph("_" * 50, signature_style))
    story.append(Paragraph("<b>Fabiano</b>", signature_style))
    story.append(Paragraph("Coordenador Financeiro", signature_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
