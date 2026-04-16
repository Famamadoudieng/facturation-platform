# factures/exports.py
import csv
import codecs
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from datetime import datetime

class FactureExport:
    """Classe pour exporter les factures en CSV et Excel"""
    
    @staticmethod
    def exporter_csv(factures, request):
        """Exporte les factures au format CSV avec UTF-8"""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="factures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        response.write(codecs.BOM_UTF8)
        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL)
        
        writer.writerow([
            'N° Facture', 'Client', 'Date facture', 'Date échéance', 
            'Type', 'Statut', 'Total HT', 'TVA', 'Total TTC', 
            'Total payé', 'Reste à payer', 'Date création'
        ])
        
        for facture in factures:
            writer.writerow([
                facture.numero,
                facture.client.nom,
                facture.date_facture.strftime('%d/%m/%Y'),
                facture.date_echeance.strftime('%d/%m/%Y'),
                facture.get_type_facture_display(),
                facture.get_statut_display(),
                f"{facture.total_ht:.2f}".replace('.', ','),
                f"{facture.montant_tva:.2f}".replace('.', ','),
                f"{facture.total_ttc:.2f}".replace('.', ','),
                f"{facture.total_paye:.2f}".replace('.', ','),
                f"{facture.reste_a_payer:.2f}".replace('.', ','),
                facture.date_creation.strftime('%d/%m/%Y %H:%M'),
            ])
        
        return response
    
    @staticmethod
    def exporter_excel(factures, request):
        """Exporte les factures au format Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Factures"
        
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="0d6efd", end_color="0d6efd", fill_type="solid")
        
        headers = [
            'N° Facture', 'Client', 'Date facture', 'Date échéance',
            'Type', 'Statut', 'Total HT', 'TVA', 'Total TTC',
            'Total payé', 'Reste à payer', 'Date création'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")
        
        for row, facture in enumerate(factures, 2):
            ws.cell(row=row, column=1, value=facture.numero)
            ws.cell(row=row, column=2, value=facture.client.nom)
            ws.cell(row=row, column=3, value=facture.date_facture.strftime('%d/%m/%Y'))
            ws.cell(row=row, column=4, value=facture.date_echeance.strftime('%d/%m/%Y'))
            ws.cell(row=row, column=5, value=facture.get_type_facture_display())
            ws.cell(row=row, column=6, value=facture.get_statut_display())
            ws.cell(row=row, column=7, value=float(facture.total_ht))
            ws.cell(row=row, column=8, value=float(facture.montant_tva))
            ws.cell(row=row, column=9, value=float(facture.total_ttc))
            ws.cell(row=row, column=10, value=float(facture.total_paye))
            ws.cell(row=row, column=11, value=float(facture.reste_a_payer))
            ws.cell(row=row, column=12, value=facture.date_creation.strftime('%d/%m/%Y %H:%M'))
            
            for col in [7, 8, 9, 10, 11]:
                ws.cell(row=row, column=col).number_format = '#,##0.00'
        
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 18
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="factures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        
        return response


class StatistiqueExport:
    """Classe pour exporter les statistiques"""
    
    @staticmethod
    def exporter_statistiques_excel(factures, request):
        """Exporte les statistiques des factures au format Excel"""
        wb = Workbook()
        ws1 = wb.active
        ws1.title = "Récapitulatif"
        
        total_factures = factures.count()
        total_ttc = sum(f.total_ttc for f in factures)
        total_paye = sum(f.total_paye for f in factures)
        total_impaye = sum(f.reste_a_payer for f in factures)
        
        factures_payees = factures.filter(statut='payee').count()
        factures_impayees = factures.filter(statut='impayee').count()
        factures_envoyees = factures.filter(statut='envoyee').count()
        factures_partiel = factures.filter(statut='partiel').count()
        
        title_font = Font(bold=True, size=14)
        header_font = Font(bold=True)
        
        ws1.cell(row=1, column=1, value="STATISTIQUES DES FACTURES")
        ws1.cell(row=1, column=1).font = title_font
        
        row = 3
        stats_data = [
            ('Nombre total de factures', f"{total_factures}"),
            ('Total TTC', f"{total_ttc:,.2f} FCFA"),
            ('Total payé', f"{total_paye:,.2f} FCFA"),
            ('Reste à payer', f"{total_impaye:,.2f} FCFA"),
            ('', ''),
            ('PAR STATUT', ''),
            ('Payées', f"{factures_payees} ({factures_payees/total_factures*100:.1f}%)" if total_factures > 0 else '0'),
            ('Impayées', f"{factures_impayees} ({factures_impayees/total_factures*100:.1f}%)" if total_factures > 0 else '0'),
            ('Envoyées', f"{factures_envoyees} ({factures_envoyees/total_factures*100:.1f}%)" if total_factures > 0 else '0'),
            ('Partiellement payées', f"{factures_partiel} ({factures_partiel/total_factures*100:.1f}%)" if total_factures > 0 else '0'),
        ]
        
        for label, value in stats_data:
            ws1.cell(row=row, column=1, value=label)
            if value:
                ws1.cell(row=row, column=2, value=value)
            row += 1
        
        ws1.column_dimensions['A'].width = 30
        ws1.column_dimensions['B'].width = 35
        
        # Feuille 2: Liste détaillée
        ws2 = wb.create_sheet("Liste détaillée")
        
        headers = ['N° Facture', 'Client', 'Date', 'Statut', 'Total TTC', 'Payé', 'Reste']
        for col, header in enumerate(headers, 1):
            ws2.cell(row=1, column=col, value=header).font = header_font
        
        for row, facture in enumerate(factures, 2):
            ws2.cell(row=row, column=1, value=facture.numero)
            ws2.cell(row=row, column=2, value=facture.client.nom)
            ws2.cell(row=row, column=3, value=facture.date_facture.strftime('%d/%m/%Y'))
            ws2.cell(row=row, column=4, value=facture.get_statut_display())
            ws2.cell(row=row, column=5, value=float(facture.total_ttc))
            ws2.cell(row=row, column=6, value=float(facture.total_paye))
            ws2.cell(row=row, column=7, value=float(facture.reste_a_payer))
            ws2.cell(row=row, column=5).number_format = '#,##0.00'
            ws2.cell(row=row, column=6).number_format = '#,##0.00'
            ws2.cell(row=row, column=7).number_format = '#,##0.00'
        
        for col in range(1, 8):
            ws2.column_dimensions[get_column_letter(col)].width = 18
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="statistiques_factures_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        wb.save(response)
        
        return response


# ✅ Fonction export comptabilité
def export_comptabilite(request):
    """Export pour la comptabilité"""
    from factures.models import Facture
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Comptabilité"
    
    header_font = Font(bold=True)
    
    headers = [
        'Date facture', 'N° Facture', 'Client', 'Total HT', 
        'TVA', 'Total TTC', 'Statut', 'Date paiement'
    ]
    
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header).font = header_font
    
    factures = Facture.objects.filter(type_facture='definitive')
    
    for row, facture in enumerate(factures, 2):
        ws.cell(row=row, column=1, value=facture.date_facture.strftime('%d/%m/%Y'))
        ws.cell(row=row, column=2, value=facture.numero)
        ws.cell(row=row, column=3, value=facture.client.nom)
        ws.cell(row=row, column=4, value=float(facture.total_ht))
        ws.cell(row=row, column=5, value=float(facture.montant_tva))
        ws.cell(row=row, column=6, value=float(facture.total_ttc))
        ws.cell(row=row, column=7, value=facture.get_statut_display())
        
        dernier_paiement = facture.paiements.filter(statut='confirme').order_by('-date_paiement').first()
        ws.cell(row=row, column=8, value=dernier_paiement.date_paiement.strftime('%d/%m/%Y') if dernier_paiement else '')
        
        for col in [4, 5, 6]:
            ws.cell(row=row, column=col).number_format = '#,##0.00'
    
    for col in range(1, 9):
        ws.column_dimensions[get_column_letter(col)].width = 18
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="export_comptabilite_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    
    return response