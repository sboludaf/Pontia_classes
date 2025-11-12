import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Initialize AWS clients
dynamodb_client = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
ANALYSIS_TABLE = os.environ['ANALYSIS_TABLE']
STATS_TABLE = os.environ['STATS_TABLE']
REGION = os.environ['REGION']

# DynamoDB tables
analysis_table = dynamodb_client.Table(ANALYSIS_TABLE)
stats_table = dynamodb_client.Table(STATS_TABLE)

def lambda_handler(event, context):
    """
    Lambda function to handle dashboard data and reports
    """
    try:
        print(f"📊 Processing dashboard request...")
        
        # Determine the operation based on the path
        path = event.get('path', '').lower()
        http_method = event.get('httpMethod', 'GET')
        
        if 'stats' in path and http_method == 'GET':
            return get_statistics(event)
        elif 'reports' in path and http_method == 'GET':
            return generate_report(event)
        elif 'dashboard' in path:
            return get_dashboard_data(event)
        else:
            return get_dashboard_data(event)
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return error_response(500, f"Internal server error: {str(e)}")

def get_statistics(event):
    """
    Get safety statistics for dashboard
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        site_id = query_params.get('site_id', 'all')
        days = int(query_params.get('days', 7))
        
        print(f"📈 Getting statistics for site: {site_id}, last {days} days")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get statistics from DynamoDB
        stats_data = get_site_statistics(site_id, start_date, end_date)
        
        # Get trend data
        trend_data = get_safety_trends(site_id, start_date, end_date)
        
        # Get top violations
        violations_data = get_top_violations(site_id, start_date, end_date)
        
        response_data = {
            'summary': stats_data,
            'trends': trend_data,
            'top_violations': violations_data,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'site_id': site_id,
            'generated_at': datetime.now().isoformat()
        }
        
        return success_response(200, response_data)
        
    except Exception as e:
        print(f"❌ Error getting statistics: {str(e)}")
        return error_response(500, f"Error getting statistics: {str(e)}")

def get_dashboard_data(event):
    """
    Get comprehensive dashboard data
    """
    try:
        print(f"📊 Getting dashboard data...")
        
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        site_id = query_params.get('site_id', 'all')
        
        # Get recent analysis results
        recent_analyses = get_recent_analyses(site_id, limit=10)
        
        # Get site overview
        site_overview = get_site_overview(site_id)
        
        # Get safety score distribution
        score_distribution = get_safety_score_distribution(site_id)
        
        # Get PPE compliance rates
        ppe_compliance = get_ppe_compliance_rates(site_id)
        
        response_data = {
            'recent_analyses': recent_analyses,
            'site_overview': site_overview,
            'score_distribution': score_distribution,
            'ppe_compliance': ppe_compliance,
            'generated_at': datetime.now().isoformat()
        }
        
        return success_response(200, response_data)
        
    except Exception as e:
        print(f"❌ Error getting dashboard data: {str(e)}")
        return error_response(500, f"Error getting dashboard data: {str(e)}")

def generate_report(event):
    """
    Generate safety compliance report
    """
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        site_id = query_params.get('site_id', 'all')
        report_type = query_params.get('type', 'summary')
        days = int(query_params.get('days', 30))
        
        print(f"📄 Generating {report_type} report for site: {site_id}, last {days} days")
        
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
        
        return success_response(200, report_data)
        
    except Exception as e:
        print(f"❌ Error generating report: {str(e)}")
        return error_response(500, f"Error generating report: {str(e)}")

def get_site_statistics(site_id, start_date, end_date):
    """
    Get aggregated statistics for a site
    """
    try:
        # Query stats table
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        total_images = 0
        analyzed_images = 0
        total_violations = 0
        safety_scores = []
        
        for date_key in date_range:
            if site_id == 'all':
                # Get all sites for this date
                response = stats_table.query(
                    IndexName='DateIndex',  # Assuming this GSI exists
                    KeyConditionExpression='date = :date',
                    ExpressionAttributeValues={':date': date_key}
                )
            else:
                # Get specific site
                response = stats_table.get_item(
                    Key={'site_id': site_id, 'date': date_key}
                )
            
            items = response.get('Items', [])
            for item in items:
                total_images += item.get('total_images', 0)
                analyzed_images += item.get('analyzed_images', 0)
                total_violations += item.get('violations_detected', 0)
                
                avg_score = item.get('avg_safety_score', 0)
                if avg_score > 0:
                    safety_scores.append(avg_score)
        
        # Calculate aggregates
        avg_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0
        compliance_rate = (analyzed_images / total_images * 100) if total_images > 0 else 0
        
        return {
            'total_images': total_images,
            'analyzed_images': analyzed_images,
            'total_violations': total_violations,
            'avg_safety_score': round(avg_safety_score, 2),
            'compliance_rate': round(compliance_rate, 2),
            'violation_rate': round((total_violations / analyzed_images * 100) if analyzed_images > 0 else 0, 2)
        }
        
    except Exception as e:
        print(f"Error getting site statistics: {str(e)}")
        return {
            'total_images': 0,
            'analyzed_images': 0,
            'total_violations': 0,
            'avg_safety_score': 0,
            'compliance_rate': 0,
            'violation_rate': 0
        }

def get_safety_trends(site_id, start_date, end_date):
    """
    Get safety score trends over time
    """
    try:
        trends = []
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            
            if site_id == 'all':
                response = stats_table.query(
                    IndexName='DateIndex',
                    KeyConditionExpression='date = :date',
                    ExpressionAttributeValues={':date': date_key}
                )
                items = response.get('Items', [])
                
                if items:
                    # Aggregate across all sites
                    total_score = sum(item.get('avg_safety_score', 0) for item in items)
                    avg_score = total_score / len(items)
                    total_violations = sum(item.get('violations_detected', 0) for item in items)
                else:
                    avg_score = 0
                    total_violations = 0
            else:
                response = stats_table.get_item(
                    Key={'site_id': site_id, 'date': date_key}
                )
                item = response.get('Item', {})
                avg_score = item.get('avg_safety_score', 0)
                total_violations = item.get('violations_detected', 0)
            
            trends.append({
                'date': date_key,
                'safety_score': round(avg_score, 2),
                'violations': total_violations
            })
            
            current_date += timedelta(days=1)
        
        return trends
        
    except Exception as e:
        print(f"Error getting safety trends: {str(e)}")
        return []

def get_top_violations(site_id, start_date, end_date):
    """
    Get most common violations
    """
    try:
        # Query analysis table for violations
        violations_count = defaultdict(int)
        
        # This is a simplified approach - in production, you'd use a GSI or scan with filters
        response = analysis_table.scan(
            FilterExpression='#status = :status AND contains(analyzed_at, :date_prefix)',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'analyzed',
                ':date_prefix': start_date.strftime('%Y-%m')
            }
        )
        
        for item in response.get('Items', []):
            if site_id != 'all' and item.get('site_id') != site_id:
                continue
                
            violations = item.get('violations', [])
            for violation in violations:
                violations_count[violation] += 1
        
        # Sort and return top violations
        top_violations = sorted(
            violations_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return [
            {'violation': violation, 'count': count}
            for violation, count in top_violations
        ]
        
    except Exception as e:
        print(f"Error getting top violations: {str(e)}")
        return []

def get_recent_analyses(site_id, limit=10):
    """
    Get recent analysis results
    """
    try:
        # Query recent analyses
        if site_id == 'all':
            response = analysis_table.scan(
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'analyzed'},
                Limit=limit
            )
        else:
            response = analysis_table.query(
                IndexName='SiteIndex',  # Assuming this GSI exists
                KeyConditionExpression='site_id = :site_id',
                ExpressionAttributeValues={':site_id': site_id},
                Limit=limit
            )
        
        items = response.get('Items', [])
        
        # Sort by analyzed_at (most recent first)
        items.sort(key=lambda x: x.get('analyzed_at', ''), reverse=True)
        
        # Format for response
        recent_analyses = []
        for item in items[:limit]:
            recent_analyses.append({
                'image_id': item.get('image_id'),
                'site_id': item.get('site_id'),
                'location': item.get('location', 'unknown'),
                'safety_score': item.get('safety_score', 0),
                'violations_count': len(item.get('violations', [])),
                'analyzed_at': item.get('analyzed_at'),
                'status': item.get('status')
            })
        
        return recent_analyses
        
    except Exception as e:
        print(f"Error getting recent analyses: {str(e)}")
        return []

def get_site_overview(site_id):
    """
    Get site overview statistics
    """
    try:
        # Get today's stats
        today = datetime.now().strftime('%Y-%m-%d')
        
        if site_id == 'all':
            response = stats_table.query(
                IndexName='DateIndex',
                KeyConditionExpression='date = :date',
                ExpressionAttributeValues={':date': today}
            )
            items = response.get('Items', [])
            
            total_sites = len(items)
            total_images = sum(item.get('total_images', 0) for item in items)
            analyzed_images = sum(item.get('analyzed_images', 0) for item in items)
            avg_safety_score = sum(item.get('avg_safety_score', 0) for item in items) / total_sites if total_sites > 0 else 0
        else:
            response = stats_table.get_item(
                Key={'site_id': site_id, 'date': today}
            )
            item = response.get('Item', {})
            
            total_sites = 1
            total_images = item.get('total_images', 0)
            analyzed_images = item.get('analyzed_images', 0)
            avg_safety_score = item.get('avg_safety_score', 0)
        
        return {
            'total_sites': total_sites,
            'total_images_today': total_images,
            'analyzed_images_today': analyzed_images,
            'current_safety_score': round(avg_safety_score, 2),
            'analysis_completion_rate': round((analyzed_images / total_images * 100) if total_images > 0 else 0, 2)
        }
        
    except Exception as e:
        print(f"Error getting site overview: {str(e)}")
        return {
            'total_sites': 0,
            'total_images_today': 0,
            'analyzed_images_today': 0,
            'current_safety_score': 0,
            'analysis_completion_rate': 0
        }

def get_safety_score_distribution(site_id):
    """
    Get distribution of safety scores
    """
    try:
        # Score ranges
        score_ranges = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0
        }
        
        # Query analyses
        response = analysis_table.scan(
            FilterExpression='#status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'analyzed'}
        )
        
        for item in response.get('Items', []):
            if site_id != 'all' and item.get('site_id') != site_id:
                continue
                
            score = item.get('safety_score', 0)
            
            if score <= 20:
                score_ranges['0-20'] += 1
            elif score <= 40:
                score_ranges['21-40'] += 1
            elif score <= 60:
                score_ranges['41-60'] += 1
            elif score <= 80:
                score_ranges['61-80'] += 1
            else:
                score_ranges['81-100'] += 1
        
        return score_ranges
        
    except Exception as e:
        print(f"Error getting score distribution: {str(e)}")
        return {range_key: 0 for range_key in ['0-20', '21-40', '41-60', '61-80', '81-100']}

def get_ppe_compliance_rates(site_id):
    """
    Get PPE compliance rates
    """
    try:
        ppe_stats = {
            'helmet': {'compliant': 0, 'total': 0},
            'vest': {'compliant': 0, 'total': 0},
            'gloves': {'compliant': 0, 'total': 0},
            'glasses': {'compliant': 0, 'total': 0},
            'boots': {'compliant': 0, 'total': 0}
        }
        
        # Query analyses
        response = analysis_table.scan(
            FilterExpression='#status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'analyzed'}
        )
        
        for item in response.get('Items', []):
            if site_id != 'all' and item.get('site_id') != site_id:
                continue
                
            ppe_detected = item.get('ppe_detected', {})
            
            for person_key, person_ppe in ppe_detected.items():
                for ppe_type in ppe_stats.keys():
                    ppe_stats[ppe_type]['total'] += 1
                    if person_ppe.get(ppe_type, False):
                        ppe_stats[ppe_type]['compliant'] += 1
        
        # Calculate compliance rates
        for ppe_type in ppe_stats:
            total = ppe_stats[ppe_type]['total']
            compliant = ppe_stats[ppe_type]['compliant']
            ppe_stats[ppe_type]['compliance_rate'] = round((compliant / total * 100) if total > 0 else 0, 2)
        
        return ppe_stats
        
    except Exception as e:
        print(f"Error getting PPE compliance rates: {str(e)}")
        return {}

def generate_summary_report(site_id, start_date, end_date):
    """
    Generate summary safety report
    """
    try:
        # Get statistics
        stats = get_site_statistics(site_id, start_date, end_date)
        
        # Get trends
        trends = get_safety_trends(site_id, start_date, end_date)
        
        # Get top violations
        violations = get_top_violations(site_id, start_date, end_date)
        
        report = {
            'report_type': 'summary',
            'site_id': site_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'executive_summary': {
                'total_images_analyzed': stats['analyzed_images'],
                'average_safety_score': stats['avg_safety_score'],
                'total_violations': stats['total_violations'],
                'compliance_rate': stats['compliance_rate']
            },
            'trends': trends,
            'top_violations': violations[:5],
            'recommendations': generate_recommendations(stats),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating summary report: {str(e)}")
        raise

def generate_detailed_report(site_id, start_date, end_date):
    """
    Generate detailed safety report
    """
    try:
        # Get summary data
        summary_report = generate_summary_report(site_id, start_date, end_date)
        
        # Add detailed analysis
        detailed_analyses = get_recent_analyses(site_id, limit=50)
        
        # Add PPE compliance breakdown
        ppe_compliance = get_ppe_compliance_rates(site_id)
        
        # Add score distribution
        score_distribution = get_safety_score_distribution(site_id)
        
        detailed_report = {
            **summary_report,
            'report_type': 'detailed',
            'detailed_analyses': detailed_analyses,
            'ppe_compliance_breakdown': ppe_compliance,
            'score_distribution': score_distribution,
            'risk_assessment': generate_risk_assessment(summary_report['executive_summary'])
        }
        
        return detailed_report
        
    except Exception as e:
        print(f"Error generating detailed report: {str(e)}")
        raise

def generate_violations_report(site_id, start_date, end_date):
    """
    Generate violations-focused report
    """
    try:
        # Get all violations
        all_violations = get_top_violations(site_id, start_date, end_date)
        
        # Get analyses with violations
        response = analysis_table.scan(
            FilterExpression='#status = :status AND size(violations) > :zero',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'analyzed', ':zero': 0}
        )
        
        violations_by_site = defaultdict(list)
        high_risk_incidents = []
        
        for item in response.get('Items', []):
            if site_id != 'all' and item.get('site_id') != site_id:
                continue
                
            site = item.get('site_id', 'unknown')
            violations = item.get('violations', [])
            safety_score = item.get('safety_score', 100)
            
            violations_by_site[site].extend(violations)
            
            # Flag high-risk incidents (low safety score)
            if safety_score < 50:
                high_risk_incidents.append({
                    'image_id': item.get('image_id'),
                    'site_id': site,
                    'location': item.get('location', 'unknown'),
                    'safety_score': safety_score,
                    'violations': violations,
                    'analyzed_at': item.get('analyzed_at')
                })
        
        violations_report = {
            'report_type': 'violations',
            'site_id': site_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'violation_summary': {
                'total_violations': sum(len(violations) for violations in violations_by_site.values()),
                'unique_violation_types': len(all_violations),
                'sites_with_violations': len(violations_by_site),
                'high_risk_incidents': len(high_risk_incidents)
            },
            'violations_by_type': all_violations,
            'violations_by_site': dict(violations_by_site),
            'high_risk_incidents': high_risk_incidents[:20],  # Top 20
            'corrective_actions': generate_corrective_actions(all_violations),
            'generated_at': datetime.now().isoformat()
        }
        
        return violations_report
        
    except Exception as e:
        print(f"Error generating violations report: {str(e)}")
        raise

def generate_recommendations(stats):
    """
    Generate safety recommendations based on statistics
    """
    recommendations = []
    
    if stats['avg_safety_score'] < 70:
        recommendations.append("Implement additional safety training programs")
    
    if stats['violation_rate'] > 30:
        recommendations.append("Increase safety supervision and monitoring")
    
    if stats['compliance_rate'] < 80:
        recommendations.append("Review and improve PPE distribution processes")
    
    if stats['total_violations'] > stats['analyzed_images'] * 0.5:
        recommendations.append("Conduct comprehensive safety audit")
    
    return recommendations

def generate_risk_assessment(summary):
    """
    Generate risk assessment based on summary data
    """
    avg_score = summary.get('average_safety_score', 100)
    violations = summary.get('total_violations', 0)
    
    if avg_score >= 90:
        risk_level = "Low"
        risk_color = "#28a745"
    elif avg_score >= 70:
        risk_level = "Medium"
        risk_color = "#ffc107"
    else:
        risk_level = "High"
        risk_color = "#dc3545"
    
    return {
        'overall_risk_level': risk_level,
        'risk_score': avg_score,
        'risk_factors': violations,
        'risk_color': risk_color,
        'immediate_action_required': avg_score < 60
    }

def generate_corrective_actions(violations):
    """
    Generate corrective actions for common violations
    """
    actions = []
    
    violation_types = [v['violation'] for v in violations]
    
    if any('helmet' in v.lower() for v in violation_types):
        actions.append("Enforce mandatory helmet policy with regular checks")
    
    if any('vest' in v.lower() for v in violation_types):
        actions.append("Ensure high-visibility vests are available and worn")
    
    if any('gloves' in v.lower() for v in violation_types):
        actions.append("Provide appropriate gloves for all tasks requiring hand protection")
    
    if any('hazard' in v.lower() for v in violation_types):
        actions.append("Conduct hazard assessment and implement mitigation measures")
    
    return list(set(actions))  # Remove duplicates

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
