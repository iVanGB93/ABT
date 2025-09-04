"""
Custom email backends for Railway-compatible email sending
"""
import requests
import json
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from decouple import config
import logging

logger = logging.getLogger(__name__)

class ResendAPIBackend(BaseEmailBackend):
    """
    Email backend that uses Resend HTTP API instead of SMTP
    Compatible with Railway and other platforms that block SMTP ports
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = config('RESEND_API_KEY', default='')
        self.api_url = 'https://api.resend.com/emails'
        
    def send_messages(self, email_messages):
        """
        Send multiple email messages using Resend API
        """
        if not email_messages:
            return 0
            
        if not self.api_key or self.api_key == 'AQUI_PONER_RESEND_API_KEY':
            logger.error("Resend API key not configured")
            if not self.fail_silently:
                raise ValueError("Resend API key not configured")
            return 0
            
        sent_count = 0
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        for message in email_messages:
            try:
                # Convert Django EmailMessage to Resend API format
                email_data = self._prepare_email_data(message)
                
                # Send via Resend API
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=email_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    sent_count += 1
                    logger.info(f"Email sent successfully to {message.to}")
                else:
                    logger.error(f"Resend API error: {response.status_code} - {response.text}")
                    if not self.fail_silently:
                        raise Exception(f"Resend API error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                if not self.fail_silently:
                    raise
                    
        return sent_count
    
    def _prepare_email_data(self, message):
        """
        Convert Django EmailMessage to Resend API format
        """
        email_data = {
            'from': message.from_email,
            'to': message.to,
            'subject': message.subject,
        }
        
        # Add CC and BCC if present
        if hasattr(message, 'cc') and message.cc:
            email_data['cc'] = message.cc
        if hasattr(message, 'bcc') and message.bcc:
            email_data['bcc'] = message.bcc
            
        # Handle HTML and text content
        if hasattr(message, 'alternatives') and message.alternatives:
            # Check for HTML alternative
            for content, content_type in message.alternatives:
                if content_type == 'text/html':
                    email_data['html'] = content
                    break
        
        # Always include text version
        if message.body:
            email_data['text'] = message.body
            
        # If no text but has HTML, add a simple text version
        if 'html' in email_data and not email_data.get('text'):
            # Simple HTML to text conversion
            import re
            text_content = re.sub('<[^<]+?>', '', email_data['html'])
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            email_data['text'] = text_content
            
        return email_data


class MailgunAPIBackend(BaseEmailBackend):
    """
    Email backend that uses Mailgun HTTP API instead of SMTP
    Alternative option for Railway compatibility
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = config('MAILGUN_API_KEY', default='')
        self.domain = config('MAILGUN_DOMAIN', default='')
        self.api_url = f'https://api.mailgun.net/v3/{self.domain}/messages'
        
    def send_messages(self, email_messages):
        """
        Send multiple email messages using Mailgun API
        """
        if not email_messages:
            return 0
            
        if not self.api_key or not self.domain:
            logger.error("Mailgun API key or domain not configured")
            if not self.fail_silently:
                raise ValueError("Mailgun API key or domain not configured")
            return 0
            
        sent_count = 0
        
        for message in email_messages:
            try:
                # Prepare email data for Mailgun
                email_data = {
                    'from': message.from_email,
                    'to': message.to,
                    'subject': message.subject,
                    'text': message.body,
                }
                
                # Add HTML if present
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, content_type in message.alternatives:
                        if content_type == 'text/html':
                            email_data['html'] = content
                            break
                
                # Send via Mailgun API
                response = requests.post(
                    self.api_url,
                    auth=('api', self.api_key),
                    data=email_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    sent_count += 1
                    logger.info(f"Email sent successfully via Mailgun to {message.to}")
                else:
                    logger.error(f"Mailgun API error: {response.status_code} - {response.text}")
                    if not self.fail_silently:
                        raise Exception(f"Mailgun API error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Failed to send email via Mailgun: {str(e)}")
                if not self.fail_silently:
                    raise
                    
        return sent_count
