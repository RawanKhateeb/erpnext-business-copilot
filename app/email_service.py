"""
Email utilities for sending approval analysis and reports
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import os


def send_approval_email(recipient_email: str, approval_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send approval analysis via email.
    
    Args:
        recipient_email: Email address to send to
        approval_data: Approval analysis data with decision, summary, findings, etc.
    
    Returns:
        {success: bool, message: str}
    """
    try:
        # Email configuration (using environment variables or defaults)
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        sender_email = os.getenv('SENDER_EMAIL', 'copilot@erpnext.local')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        
        # Build email content
        decision = approval_data.get('decision', 'UNKNOWN')
        summary = approval_data.get('summary', '')
        po_name = approval_data.get('po_data', {}).get('name', 'Unknown PO')
        
        # HTML email body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Purchase Order Approval Analysis</h2>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">PO: {po_name}</h3>
                    <p><strong>Decision:</strong> <span style="
                        padding: 8px 15px;
                        border-radius: 4px;
                        font-weight: bold;
                        {'background: #d4edda; color: #155724;' if decision == 'APPROVE' else ''}
                        {'background: #fff3cd; color: #856404;' if decision == 'REVIEW' else ''}
                        {'background: #f8d7da; color: #721c24;' if decision == 'DO NOT APPROVE' else ''}
                    ">{decision}</span></p>
                    <p><strong>Summary:</strong></p>
                    <p>{summary}</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h4>Findings:</h4>
                    <ul style="line-height: 1.8;">
        """
        
        findings = approval_data.get('findings', [])
        for finding in findings:
            html_body += f"<li>{finding}</li>"
        
        html_body += """
                    </ul>
                </div>
                
                <div style="margin: 20px 0;">
                    <h4>Evidence:</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                        <thead>
                            <tr style="background: #667eea; color: white;">
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Item Code</th>
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Rate</th>
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Avg Rate</th>
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Delta</th>
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        evidence = approval_data.get('evidence', [])
        for item in evidence:
            html_body += f"""
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 10px;">{item.get('item_code', 'N/A')}</td>
                                <td style="padding: 10px;">{item.get('rate', 'N/A')}</td>
                                <td style="padding: 10px;">{item.get('avg_rate', 'N/A')}</td>
                                <td style="padding: 10px;">{item.get('delta', 'N/A')}</td>
                                <td style="padding: 10px;">
                                    <span style="
                                        padding: 4px 8px;
                                        border-radius: 4px;
                                        font-weight: 600;
                                        {'background: #f8d7da; color: #721c24;' if 'ANOMALY' in item.get('status', '') else 'background: #d4edda; color: #155724;'}
                                        font-size: 11px;
                                    ">{item.get('status', '✓')}</span>
                                </td>
                            </tr>
            """
        
        html_body += """
                        </tbody>
                    </table>
                </div>
                
                <div style="margin: 20px 0;">
                    <h4>Recommended Actions:</h4>
                    <ul style="line-height: 1.8;">
        """
        
        actions = approval_data.get('next_actions', [])
        for action in actions:
            html_body += f"<li>{action}</li>"
        
        html_body += """
                    </ul>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">
                    This email was generated by ERPNext Copilot Approval Assistant.<br>
                    Please do not reply to this email.
                </p>
            </body>
        </html>
        """
        
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = f"PO Approval Analysis: {po_name} - {decision}"
        message['From'] = sender_email
        message['To'] = recipient_email
        
        # Attach HTML body
        message.attach(MIMEText(html_body, 'html'))
        
        # Send email
        try:
            # Try SMTP with TLS
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if sender_password:
                    server.login(sender_email, sender_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': f'Approval analysis sent to {recipient_email}'
            }
        except smtplib.SMTPAuthenticationError:
            # Try without authentication (local server)
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(message)
            
            return {
                'success': True,
                'message': f'Approval analysis sent to {recipient_email}'
            }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }


def send_report_email(recipient_email: str, report_data: Dict[str, Any], report_type: str = 'report') -> Dict[str, Any]:
    """
    Send any report via email.
    
    Args:
        recipient_email: Email address to send to
        report_data: Report data
        report_type: Type of report (approval, monthly, pending, etc.)
    
    Returns:
        {success: bool, message: str}
    """
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'localhost')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        sender_email = os.getenv('SENDER_EMAIL', 'copilot@erpnext.local')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        
        # Simple HTML body for generic reports
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>{report_type.upper()} Report</h2>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word;">
{str(report_data)}
                    </pre>
                </div>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">
                    This email was generated by ERPNext Copilot.<br>
                    Please do not reply to this email.
                </p>
            </body>
        </html>
        """
        
        message = MIMEMultipart('alternative')
        message['Subject'] = f"ERPNext Copilot - {report_type.capitalize()} Report"
        message['From'] = sender_email
        message['To'] = recipient_email
        message.attach(MIMEText(html_body, 'html'))
        
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if sender_password:
                    server.login(sender_email, sender_password)
                server.send_message(message)
        except smtplib.SMTPAuthenticationError:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(message)
        
        return {
            'success': True,
            'message': f'Report sent to {recipient_email}'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }
