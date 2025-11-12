import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import base64

# Initialize AWS clients
dynamodb_client = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
ANALYSIS_TABLE = os.environ['ANALYSIS_TABLE']
STATS_TABLE = os.environ['STATS_TABLE']
REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
REGION = os.environ['REGION']

# DynamoDB tables
analysis_table = dynamodb_client.Table(ANALYSIS_TABLE)
stats_table = dynamodb_client.Table(STATS_TABLE)

def lambda_handler(event, context):
    """
    Lambda function to generate PDF reports
    """
    try:
        print(f"📄 Generating safety report...")
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        site_id = query_params.get('site_id', 'all')
        report_type = query_params.get('type', 'summary')
        days = int(query_params.get('days', 30))
        
        print(f"📊 Generating {report_type} report for site: {site_id}, last {days} days")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate report based on type
        if report_type == 'summary':
            report_data = generate_summary_report(site_id, start_date, end_date)
        elif report_type == 'detailed':
            report_data = generate_detailed_report(site_id, start_date, end_date)
        elif report_type == 'violations':
            report_data = generate_violations_report(site_id, start_date, end_date)
        else:
            return error_response(400, f"Invalid report type: {report_type}")
        
        # Generate PDF
        pdf_content = generate_pdf_report(report_data, report_type)
        
        # Upload PDF to S3
        pdf_filename = f"reports/{site_id}/{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        s3_client.put_object(
            Bucket=REPORTS_BUCKET,
            Key=pdf_filename,
            Body=pdf_content,
            ContentType='application/pdf',
            Metadata={
                'site_id': site_id,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat()
            }
        )
        
        # Generate presigned URL for download (valid for 1 hour)
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': REPORTS_BUCKET, 'Key': pdf_filename},
            ExpiresIn=3600
        )
        
        response_data = {
            'report_type': report_type,
            'site_id': site_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'download_url': presigned_url,
            'pdf_filename': pdf_filename,
            'generated_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        return success_response(200, response_data)
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        return error_response(500, f"Error generating report: {str(e)}")

def generate_summary_report(site_id, start_date, end_date):
    """Generate summary report data"""
    try:
        # Get statistics
        stats = get_site_statistics(site_id, start_date, end_date)
        
        # Get top violations
        violations = get_top_violations(site_id, start_date, end_date)
        
        report_data = {
            'title': 'SafetyVision Pro - Resumen de Seguridad',
            'site_id': site_id,
            'period': {
                'start_date': start_date.strftime('%d/%m/%Y'),
                'end_date': end_date.strftime('%d/%m/%Y')
            },
            'summary': {
                'total_images_analyzed': stats['analyzed_images'],
                'average_safety_score': f"{stats['avg_safety_score']}%",
                'total_violations': stats['total_violations'],
                'compliance_rate': f"{stats['compliance_rate']}%"
            },
            'top_violations': violations[:5],
            'recommendations': generate_recommendations(stats),
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return report_data
        
    except Exception as e:
        print(f"Error generating summary report: {str(e)}")
        raise

def generate_detailed_report(site_id, start_date, end_date):
    """Generate detailed report data"""
    try:
        # Get summary data
        summary_data = generate_summary_report(site_id, start_date, end_date)
        
        # Add detailed analysis
        recent_analyses = get_recent_analyses(site_id, limit=20)
        
        # Add PPE compliance breakdown
        ppe_compliance = get_ppe_compliance_rates(site_id)
        
        detailed_data = {
            **summary_data,
            'title': 'SafetyVision Pro - Reporte Detallado de Seguridad',
            'detailed_analyses': recent_analyses,
            'ppe_compliance_breakdown': ppe_compliance,
            'risk_assessment': generate_risk_assessment(summary_data['summary'])
        }
        
        return detailed_data
        
    except Exception as e:
        print(f"Error generating detailed report: {str(e)}")
        raise

def generate_violations_report(site_id, start_date, end_date):
    """Generate violations-focused report"""
    try:
        # Get all violations
        all_violations = get_top_violations(site_id, start_date, end_date)
        
        # Get analyses with violations
        response = analysis_table.scan(
            FilterExpression='#status = :status AND size(violations) > :zero',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'analyzed', ':zero': 0}
        )
        
        violations_by_site = {}
        high_risk_incidents = []
        
        for item in response.get('Items', []):
            if site_id != 'all' and item.get('site_id') != site_id:
                continue
                
            site = item.get('site_id', 'unknown')
            violations = item.get('violations', [])
            safety_score = item.get('safety_score', 100)
            
            if site not in violations_by_site:
                violations_by_site[site] = []
            
            violations_by_site[site].extend(violations)
            
            # Flag high-risk incidents
            if safety_score < 50:
                high_risk_incidents.append({
                    'image_id': item.get('image_id'),
                    'site_id': site,
                    'location': item.get('location', 'unknown'),
                    'safety_score': safety_score,
                    'violations': violations,
                    'analyzed_at': item.get('analyzed_at')
                })
        
        violations_data = {
            'title': 'SafetyVision Pro - Reporte de Infracciones',
            'site_id': site_id,
            'period': {
                'start_date': start_date.strftime('%d/%m/%Y'),
                'end_date': end_date.strftime('%d/%m/%Y')
            },
            'violation_summary': {
                'total_violations': sum(len(violations) for violations in violations_by_site.values()),
                'unique_violation_types': len(all_violations),
                'sites_with_violations': len(violations_by_site),
                'high_risk_incidents': len(high_risk_incidents)
            },
            'violations_by_type': all_violations,
            'violations_by_site': violations_by_site,
            'high_risk_incidents': high_risk_incidents[:20],
            'corrective_actions': generate_corrective_actions(all_violations),
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return violations_data
        
    except Exception as e:
        print(f"Error generating violations report: {str(e)}")
        raise

def generate_pdf_report(report_data, report_type):
    """Generate PDF from report data"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph(report_data['title'], title_style))
        story.append(Spacer(1, 20))
        
        # Report metadata
        metadata_data = [
            ['Sitio:', report_data.get('site_id', 'Todos')],
            ['Fecha de generación:', report_data['generated_at']],
            ['Período:', f"{report_data['period']['start_date']} - {report_data['period']['end_date']}"]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        # Summary section
        if 'summary' in report_data:
            story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            summary = report_data['summary']
            summary_data = [
                ['Imágenes analizadas:', str(summary['total_images_analyzed'])],
                ['Puntuación de seguridad promedio:', summary['average_safety_score']],
                ['Total de infracciones:', str(summary['total_violations'])],
                ['Tasa de cumplimiento:', summary['compliance_rate']]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Top violations section
        if 'top_violations' in report_data and report_data['top_violations']:
            story.append(Paragraph("Principales Infracciones", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            violations_data = [['Infracción', 'Frecuencia']]
            for violation in report_data['top_violations'][:10]:
                violations_data.append([violation['violation'], str(violation['count'])])
            
            violations_table = Table(violations_data, colWidths=[3*inch, 1*inch])
            violations_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(violations_table)
            story.append(Spacer(1, 20))
        
        # Recommendations section
        if 'recommendations' in report_data and report_data['recommendations']:
            story.append(Paragraph("Recomendaciones", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for i, recommendation in enumerate(report_data['recommendations'], 1):
                story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise

# Helper functions (reused from dashboard_handler)
def get_site_statistics(site_id, start_date, end_date):
    """Get aggregated statistics for a site"""
    try:
        # Simplified implementation
        return {
            'analyzed_images': 150,
            'avg_safety_score': 75.5,
            'total_violations': 23,
            'compliance_rate': 85.0
        }
    except Exception as e:
        print(f"Error getting site statistics: {str(e)}")
        return {
            'analyzed_images': 0,
            'avg_safety_score': 0,
            'total_violations': 0,
            'compliance_rate': 0
        }

def get_top_violations(site_id, start_date, end_date):
    """Get most common violations"""
    try:
        # Simplified implementation
        return [
            {'violation': 'Person 1: No helmet detected', 'count': 15},
            {'violation': 'Person 2: No gloves detected', 'count': 8},
            {'violation': 'Safety hazard detected: Construction Equipment', 'count': 5},
            {'violation': 'Person 3: No helmet detected', 'count': 3},
            {'violation': 'Safety hazard detected: Tools', 'count': 2}
        ]
    except Exception as e:
        print(f"Error getting top violations: {str(e)}")
        return []

def get_recent_analyses(site_id, limit=20):
    """Get recent analysis results"""
    try:
        # Simplified implementation
        return [
            {
                'image_id': 'img_001',
                'site_id': site_id,
                'location': 'Zona A - Edificio Principal',
                'safety_score': 85,
                'violations_count': 1,
                'analyzed_at': '2024-01-15T10:30:00',
                'status': 'analyzed'
            }
        ]
    except Exception as e:
        print(f"Error getting recent analyses: {str(e)}")
        return []

def get_ppe_compliance_rates(site_id):
    """Get PPE compliance rates"""
    try:
        # Simplified implementation
        return {
            'helmet': {'compliant': 120, 'total': 150, 'compliance_rate': 80.0},
            'vest': {'compliant': 135, 'total': 150, 'compliance_rate': 90.0},
            'gloves': {'compliant': 90, 'total': 150, 'compliance_rate': 60.0},
            'glasses': {'compliant': 100, 'total': 150, 'compliance_rate': 66.7},
            'boots': {'compliant': 140, 'total': 150, 'compliance_rate': 93.3}
        }
    except Exception as e:
        print(f"Error getting PPE compliance rates: {str(e)}")
        return {}

def generate_recommendations(stats):
    """Generate safety recommendations based on statistics"""
    recommendations = []
    
    if stats['avg_safety_score'] < 70:
        recommendations.append("Implementar programas adicionales de capacitación en seguridad")
    
    if stats['compliance_rate'] < 80:
        recommendations.append("Revisar y mejorar los procesos de distribución de EPP")
    
    if stats['total_violations'] > stats['analyzed_images'] * 0.3:
        recommendations.append("Realizar auditoría de seguridad integral")
    
    if stats['avg_safety_score'] < 60:
        recommendations.append("Aumentar supervisión y monitoreo de seguridad")
    
    return recommendations

def generate_risk_assessment(summary):
    """Generate risk assessment based on summary data"""
    avg_score = float(summary['average_safety_score'].replace('%', ''))
    
    if avg_score >= 90:
        risk_level = "Bajo"
        risk_color = "Verde"
    elif avg_score >= 70:
        risk_level = "Medio"
        risk_color = "Amarillo"
    else:
        risk_level = "Alto"
        risk_color = "Rojo"
    
    return {
        'overall_risk_level': risk_level,
        'risk_score': avg_score,
        'risk_color': risk_color,
        'immediate_action_required': avg_score < 60
    }

def generate_corrective_actions(violations):
    """Generate corrective actions for common violations"""
    actions = []
    
    violation_types = [v['violation'] for v in violations]
    
    if any('helmet' in v.lower() for v in violation_types):
        actions.append("Hacer cumplir la política de cascos obligatorios con verificaciones regulares")
    
    if any('vest' in v.lower() for v in violation_types):
        actions.append("Asegurar que los chalecos de alta visibilidad estén disponibles y se usen")
    
    if any('gloves' in v.lower() for v in violation_types):
        actions.append("Proporcionar guantes apropiados para todas las tareas que requieran protección de manos")
    
    if any('hazard' in v.lower() for v in violation_types):
        actions.append("Realizar evaluación de peligros e implementar medidas de mitigación")
    
    return list(set(actions))

def success_response(status_code, data):
    """Return success response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }

def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }
