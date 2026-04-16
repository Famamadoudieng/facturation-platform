# factures/views_pdf.py
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, BaseDocTemplate, PageTemplate, Frame
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Facture
from parametres.models import ParametresEntreprise
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak
from parametres.models import ParametresFacturation
from pypdf import PdfReader
import os

# ✅ Fonction simple pour la numérotation
def add_page_number(canvas, doc):
    """Ajoute le numéro de page"""
    page_num = canvas.getPageNumber()
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 10, f"page {page_num}")
    canvas.restoreState()



@login_required
def generer_pdf_facture(request, pk):
    """Génère le PDF d'une facture"""
    facture = get_object_or_404(Facture, pk=pk)
    
    # ✅ Récupérer les paramètres de l'entreprise courante
    if hasattr(request, 'entreprise_courante') and request.entreprise_courante:
        entreprise_params = ParametresEntreprise.objects.filter(entreprise=request.entreprise_courante).first()
    else:
        entreprise_params = ParametresEntreprise.get_instance()

    

    # Récupérer les paramètres de facturation
    if hasattr(request, 'entreprise_courante') and request.entreprise_courante:
        facturation_params = ParametresFacturation.objects.filter(entreprise=request.entreprise_courante).first()
    else:
        facturation_params = ParametresFacturation.get_instance()
    

    # ✅ 1. Créer le buffer
    buffer = BytesIO()
    # ✅ SimpleDocTemplate standard
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.2*cm,
        leftMargin=0.2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )
    
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.HexColor('#d4a23f'),
        alignment=0,
        spaceAfter=0,
        leading=20,
        fontName= 'Times-Roman', #'Helvetica',
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#808080'),
        alignment=0,
        fontName='Times-Roman', #'Helvetica',
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName='Times-Roman', #'Helvetica',
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#d4a23f'),
        fontName='Times-Bold',#'Helvetica-Bold',
        spaceAfter=5,
    )

    pres_style= ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontSize=10,
        #textColor=colors.HexColor('#d96000'),
        fontName='Times-Bold', #'Helvetica-Bold',
        spaceAfter=5,
    )
    
    
    elements = []
    
    # === EN-TÊTE AVEC LOGO ===
    # === EN-TÊTE AVEC LOGO ===
    logo_path = None
    if entreprise_params and entreprise_params.logo:
        logo_path = entreprise_params.logo.path
        if not os.path.exists(logo_path):
            logo_path = None

    # Créer le texte du titre avec la date en dessous
    if facture.type_facture == 'proforma':
        titre_texte = f"FACTURE PROFORMA N° {facture.numero}<br/><font size=9 color='#7f8c8d'> {facture.date_facture.strftime('%d/%m/%Y')}</font>"
    else:
        titre_texte = f"FACTURE DÉFINITIVE N° {facture.numero}<br/><font size=9 color='#7f8c8d'>{facture.date_facture.strftime('%d/%m/%Y')}</font><br/><font size=9 color='#d4a23f'>Statut: {facture.get_statut_display()}</font>"
        #titre_texte = f"FACTURE DÉFINITIVE N° {facture.numero}<br/><font size=9 color='#7f8c8d'>{facture.date_facture.strftime('%d/%m/%Y')}</font>"

    titre = Paragraph(titre_texte, title_style)

    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=80, height=60)
            header_table = Table([[titre, logo]], colWidths=[480, 100])
        except Exception as e:
            print(f"Erreur logo: {e}")
            header_table = Table([[titre]], colWidths=[480])
    else:
        header_table = Table([[titre]], colWidths=[480])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 15))  # Petit espace après l'en-tête
  
# === ÉMETTEUR ET DESTINATAIRE ===
# Tableau pour l'émetteur
    if entreprise_params:
        emetteur_data = [
            [Paragraph('Emetteur', section_style), ''],
            [Paragraph('Société:', date_style), entreprise_params.nom_entreprise.upper()],
            [Paragraph('Adresse:', date_style), Paragraph(entreprise_params.adresse.replace('/', '<br/>'), info_style)],
            [Paragraph('Pays:', date_style), entreprise_params.pays],
            [Paragraph('Numéro d\'entreprise:', date_style), entreprise_params.siret or '-'],
            [Paragraph('Numéro de TVA:', date_style), f"{facturation_params.tva_par_defaut}"],
            [Paragraph('Numéro de téléphone:', date_style), Paragraph(entreprise_params.telephone.replace('/', '<br/>'), info_style)],
            [Paragraph('Adresse email:', date_style), entreprise_params.email],
        ]
    
        # Ajuster la largeur des colonnes
        emetteur_table = Table(emetteur_data, colWidths=[100, doc.width/2 - 100])
        emetteur_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
    else:
        emetteur_table = Paragraph("<b>Emetteur</b><br/>Informations non disponibles", info_style)

    # Tableau pour le destinataire
    destinataire_data = [
        [Paragraph('Destinataire', section_style), ''],
        [Paragraph('Société/Client:', date_style), Paragraph(facture.client.nom, info_style)],
        #[Paragraph('Adresse:', date_style), facture.client.adresse or ''],
        [Paragraph('Adresse:', date_style), Paragraph(facture.client.adresse or '', info_style)],
        #['Adresse:', facture.client.adresse or ''],
        #['Email:', facture.client.email or ''],
        [Paragraph('Email:', date_style), facture.client.email or ''],
        #['Tél:', facture.client.telephone or ''],
        [Paragraph('Tél:', date_style), facture.client.telephone or '']

    ]

    destinataire_table = Table(destinataire_data, colWidths=[80, doc.width/2 - 100])
    destinataire_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    # Tableau principal avec émetteur et destinataire côte à côte
    info_table = Table(
        [[emetteur_table, destinataire_table]],
        colWidths=[doc.width/2 - 10, doc.width/2 - 10]
    )
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # === PRESTATION ===
    if facture.notes:
        elements.append(Paragraph(f"<b>Prestation:</b> {facture.notes}", pres_style))
        elements.append(Spacer(1, 15))
    
    # === TABLEAU DES PRODUITS ===
    elements.append(Paragraph("<b>Détail</b>", section_style))
    elements.append(Spacer(1, 5))
    
    table_data = [['Type', 'Description', 'Prix unitaire', 'Qté', 'Total HT']]
    
    for ligne in facture.lignes.all():
        table_data.append([
            Paragraph(ligne.designation[:40], info_style),
            Paragraph(ligne.designation, info_style),
            f"{ligne.prix_unitaire_ht:,.2f} CFA".replace(',', ' '),
            str(ligne.quantite),
            f"{ligne.total_ht:,.2f} CFA".replace(',', ' '),
        ])
    
    col_widths = [150, doc.width * 0.35, 80, 50, 100]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d4a23f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Ou spécifiquement pour les lignes de données (lignes 1 à la fin) hauteur cellule
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
        # === TOTAUX ===
    totals_data = [
        ['Total HT', f"{facture.total_ht:,.2f} CFA".replace(',', ' ')],
        [f'TVA ({facture.taux_tva}%)', f"{facture.montant_tva:,.2f} CFA".replace(',', ' ')],
        #['', ''],
        ['Total TTC', f"{facture.total_ttc:,.2f} CFA".replace(',', ' ')],
    ]

    # ✅ Ajouter les acomptes s'ils existent
    if facture.total_paye > 0:
        #totals_data.append(['', ''])
        totals_data.append(['Acompte versé', f"{facture.total_paye:,.2f} CFA".replace(',', ' ')])
        totals_data.append(['Reste à payer', f"{facture.reste_a_payer:,.2f} CFA".replace(',', ' ')])

    totals_table = Table(totals_data, colWidths=[doc.width - 150, 100])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, 1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, 2), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, 2), colors.HexColor('#d4a23f')),
       # ('FONTSIZE', (0, 3), (1, 3), 12),
        #('TEXTCOLOR', (0, 3), (1, 3), colors.HexColor('#e74c3c')),
        ('TOPPADDING', (0, 4), (1, 4), 10),
    ]))

    # ✅ Style pour les acomptes
    if facture.total_paye > 0:
        totals_table.setStyle(TableStyle([
            #('FONTNAME', (0, 4), (1, 4), 'Helvetica'),
            ('FONTNAME', (0, 0), (0, 4), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, 4), colors.HexColor('#d4a23f')),
            #('TOPPADDING', (0, 4), (1, 4), 5),
        ]))

    # ✅ Zébrurage : alternance des couleurs pour les lignes impaires/paires
    for i in range(1, len(table_data)):
        if i % 2 == 1:  # Lignes impaires (1, 3, 5...)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.white),  # Blanc
            ]))
        else:  # Lignes paires (2, 4, 6...)
            table.setStyle(TableStyle([
                
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0F0F2')),  # Gris clair
            ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 20))


        # === SAUT DE PAGE ===
    elements.append(PageBreak())

    # === CONDITIONS (dernière page) ===
    # Titre de la page
    conditions_title = Paragraph("<b>CONDITIONS DE RÈGLEMENT</b>", section_style)
    elements.append(conditions_title)
    elements.append(Spacer(1, 5))

    # Contenu des conditions
    conditions_text = f"""
    <b>Mode de paiement :</b>Chèque, virement bancaire, cash<br/>
    
    <b>Condition de règlements :</b>{facture.conditions} <br/>
    """

    if entreprise_params.mentions_legales:
        conditions_text += f"<b>Conditions d'annulation :</b><br/>{entreprise_params.mentions_legales.replace('\n', '<br/>')}<br/>"

    #if facture.conditions:
       # conditions_text += f"<br/><b>Conditions :</b> {facture.conditions}<br/>"
# info banque
    if entreprise_params and entreprise_params.iban:
        conditions_text += f"""
    <br/>
    <b>Information du bénéficiaire  :</b><br/>
    {entreprise_params.rcs or '-'}<br/>
    <b>Informations bancaires :</b><br/>
    
    {entreprise_params.banque or '-'}<br/>
    Code banque: {entreprise_params.bic.replace('/', '<br/>') if entreprise_params.bic else '-'}<br/>
   
    Numéro de compte: {entreprise_params.iban.replace('/', '<br/>') if entreprise_params.iban else '-'}<br/>
    Device: XOF<br/>
    """
    if entreprise_params.pied_page_facture:
        # Remplacer les retours à la ligne par <br/>
        pied_page_text = entreprise_params.pied_page_facture.replace('\n', '<br/>').replace('\r\n', '<br/>')
        conditions_text += f"<br/><b>PRESENTATION DE {entreprise_params.nom_entreprise.upper()} :</b><br/>{pied_page_text}<br/>"


    conditions_paragraph = Paragraph(conditions_text, info_style)
    elements.append(conditions_paragraph)

    # Ajouter un espace en bas de page
    #elements.append(Spacer(1, 50))

    # === IMAGES (grille 2x2) ===


    # Récupérer les 4 images
    images = []
    for i in range(1, 5):
        img_field = getattr(entreprise_params, f'image_{i}', None)
        if img_field and os.path.exists(img_field.path):
            try:
                img = Image(img_field.path, width=220, height=100)
                images.append(img)
            except:
                images.append(None)
        else:
            images.append(None)



    # Créer la grille 2x2
    grid_data = [
        [images[0] or '', images[1] or ''],
        [images[2] or '', images[3] or '']
    ]

    # Créer le tableau
    img_table = Table(grid_data, colWidths=[doc.width/2, doc.width/2])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),  # Bordure
    ]))

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<b>Galerie d'images</b>", section_style))
    elements.append(Spacer(1, 10))
    elements.append(img_table)
    
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # === CONSTRUCTION DU PDF AVEC NUMÉROTATION ===
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="facture_{facture.numero}.pdf"'
    
    return response


@login_required
def telecharger_pdf_facture(request, pk):
    """Télécharge le PDF d'une facture"""
    response = generer_pdf_facture(request, pk)
    response['Content-Disposition'] = response['Content-Disposition'].replace('inline', 'attachment')
    return response