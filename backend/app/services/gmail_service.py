import asyncio
import base64
import os
from email.mime.text import MIMEText
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from app.models.draft import Draft
from app.models.db_models import UserCredentialsDB
from app.services.email_provider import EmailProvider
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)

class GmailProvider(EmailProvider):
    """
    Implementation of EmailProvider for Google Gmail.
    """
    SCOPES = ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send']

    def __init__(self, db: Session, user_email: str):
        self.db = db
        self.user_email = user_email
        self.settings = get_settings()
        self.creds = None
        self.service = None

    async def _get_service(self):
        if self.service:
            return self.service
        
        if not self.creds:
            # Fetch from DB
            db_creds = self.db.query(UserCredentialsDB).filter(UserCredentialsDB.email == self.user_email).first()
            if not db_creds:
                raise Exception(f"No credentials found for {self.user_email}. User must authenticate via OAuth2.")
            
            self.creds = Credentials(
                token=db_creds.access_token,
                refresh_token=db_creds.refresh_token,
                token_uri=db_creds.token_uri,
                client_id=db_creds.client_id,
                client_secret=db_creds.client_secret,
                scopes=db_creds.scopes
            )

        # Refresh token if expired
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            # Update DB with new token
            db_creds = self.db.query(UserCredentialsDB).filter(UserCredentialsDB.email == self.user_email).first()
            if db_creds:
                db_creds.access_token = self.creds.token
                db_creds.expiry = self.creds.expiry
                self.db.commit()
        
        self.service = build('gmail', 'v1', credentials=self.creds)
        return self.service

    async def create_draft(self, draft: Draft) -> str:
        service = await self._get_service()
        message = MIMEText(draft.body)
        message['to'] = draft.professor_email
        message['subject'] = draft.subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        draft_body = {'message': {'raw': raw_message}}
        
        # Run synchronous execute() in a thread pool
        loop = asyncio.get_event_loop()
        created_draft = await loop.run_in_executor(
            None, 
            lambda: service.users().drafts().create(userId='me', body=draft_body).execute()
        )
        return created_draft['id']

    async def send_draft(self, draft_id: str) -> str:
        service = await self._get_service()
        
        # Run synchronous execute() in a thread pool
        loop = asyncio.get_event_loop()
        sent_message = await loop.run_in_executor(
            None,
            lambda: service.users().drafts().send(userId='me', body={'id': draft_id}).execute()
        )
        return sent_message['id']
