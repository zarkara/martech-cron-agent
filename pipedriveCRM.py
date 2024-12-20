import aiohttp
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
from dataclasses import dataclass
import json

class PipedriveClient:
    """
    Async client for Pipedrive CRM API integration.
    """
    def __init__(self, api_token: str, base_url: str = "https://api.pipedrive.com/v1"):
        self.api_token = api_token
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make authenticated request to Pipedrive API.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params['api_token'] = self.api_token

        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"Pipedrive API error: {str(e)}")
            raise

    async def create_person(self, lead_data: Dict) -> Dict:
        """
        Create a person in Pipedrive.
        """
        person_data = {
            'name': lead_data.get('contact_name', 'Unknown'),
            'email': [{'value': lead_data['email'], 'primary': True}],
            'phone': [{'value': lead_data.get('phone', ''), 'primary': True}],
            'org_id': lead_data.get('organization_id'),
            'visible_to': 3,  # Visible to entire company
            'custom_fields': {
                'linkedin_url': lead_data.get('linkedin_url', ''),
                'interest_level': lead_data.get('interest_level', ''),
                'source_platform': lead_data.get('platform', '')
            }
        }
        return await self._make_request('POST', 'persons', data=person_data)

    async def create_organization(self, company_data: Dict) -> Dict:
        """
        Create an organization in Pipedrive.
        """
        org_data = {
            'name': company_data['company_name'],
            'visible_to': 3,
            'custom_fields': {
                'industry': company_data.get('industry', ''),
                'employee_count': company_data.get('employee_count', 0),
                'estimated_revenue': company_data.get('estimated_revenue', 0),
                'linkedin_company_url': company_data.get('linkedin_url', '')
            }
        }
        return await self._make_request('POST', 'organizations', data=org_data)

    async def create_deal(self, lead_data: Dict, person_id: int, org_id: int) -> Dict:
        """
        Create a deal in Pipedrive.
        """
        deal_data = {
            'title': f"Payment Processing Solution - {lead_data['company_name']}",
            'person_id': person_id,
            'org_id': org_id,
            'stage_id': 1,  # Initial contact stage
            'visible_to': 3,
            'expected_value': self._calculate_deal_value(lead_data),
            'custom_fields': {
                'lead_source': lead_data.get('platform', ''),
                'initial_interest': lead_data.get('interest_level', ''),
                'response_content': lead_data.get('initial_response', '')
            }
        }
        return await self._make_request('POST', 'deals', data=deal_data)

    async def add_note(self, deal_id: int, content: str) -> Dict:
        """
        Add a note to a deal in Pipedrive.
        """
        note_data = {
            'deal_id': deal_id,
            'content': content,
            'pinned_to_deal_flag': 1
        }
        return await self._make_request('POST', 'notes', data=note_data)

    async def create_activity(
        self,
        deal_id: int,
        activity_type: str,
        subject: str,
        due_date: datetime
    ) -> Dict:
        """
        Create an activity (task) in Pipedrive.
        """
        activity_data = {
            'deal_id': deal_id,
            'subject': subject,
            'type': activity_type,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'due_time': due_date.strftime('%H:%M'),
            'duration': '00:30'
        }
        return await self._make_request('POST', 'activities', data=activity_data)

    def _calculate_deal_value(self, lead_data: Dict) -> float:
        """
        Calculate expected deal value based on company size and industry.
        """
        base_value = 5000  # Base monthly processing value
        
        # Adjust based on company size
        employee_multiplier = {
            range(1, 50): 1,
            range(50, 200): 2,
            range(200, 500): 3,
            range(500, 1000): 4
        }
        
        for size_range, multiplier in employee_multiplier.items():
            if lead_data.get('employee_count', 0) in size_range:
                base_value *= multiplier
                break

        # Adjust based on industry
        industry_multiplier = {
            'retail': 1.2,
            'hospitality': 1.3,
            'healthcare': 1.1,
            'professional_services': 0.9
        }
        
        industry = lead_data.get('industry', '').lower()
        base_value *= industry_multiplier.get(industry, 1.0)
        
        return base_value

