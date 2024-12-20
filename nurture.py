class NurtureSequence:
    """
    Manages automated nurture sequences for leads.
    """
    def __init__(
        self,
        pipedrive_client: PipedriveClient,
        content_generator,
        social_poster
    ):
        self.pipedrive = pipedrive_client
        self.content_generator = content_generator
        self.social_poster = social_poster
        self.logger = logging.getLogger(__name__)

        # Define nurture sequence steps
        self.sequence_steps = {
            'high_intent': [
                {
                    'delay': timedelta(days=1),
                    'type': 'personalized_content',
                    'template': 'value_proposition'
                },
                {
                    'delay': timedelta(days=3),
                    'type': 'case_study',
                    'template': 'industry_specific'
                },
                {
                    'delay': timedelta(days=7),
                    'type': 'demo_invitation',
                    'template': 'product_demo'
                }
            ],
            'medium_intent': [
                {
                    'delay': timedelta(days=2),
                    'type': 'educational_content',
                    'template': 'industry_insights'
                },
                {
                    'delay': timedelta(days=5),
                    'type': 'social_proof',
                    'template': 'testimonials'
                },
                {
                    'delay': timedelta(days=10),
                    'type': 'value_proposition',
                    'template': 'cost_savings'
                }
            ],
            'low_intent': [
                {
                    'delay': timedelta(days=3),
                    'type': 'thought_leadership',
                    'template': 'industry_trends'
                },
                {
                    'delay': timedelta(days=7),
                    'type': 'educational_content',
                    'template': 'best_practices'
                },
                {
                    'delay': timedelta(days=14),
                    'type': 'soft_pitch',
                    'template': 'discovery_invitation'
                }
            ]
        }

    async def initiate_sequence(
        self,
        lead_data: Dict,
        sequence_type: str = 'medium_intent'
    ) -> str:
        """
        Start a nurture sequence for a lead.
        """
        try:
            # Create or update Pipedrive records
            org = await self.pipedrive.create_organization(lead_data)
            person = await self.pipedrive.create_person({**lead_data, 'organization_id': org['id']})
            deal = await self.pipedrive.create_deal(lead_data, person['id'], org['id'])

            # Schedule sequence steps
            sequence = self.sequence_steps[sequence_type]
            current_time = datetime.now()

            for step in sequence:
                execution_time = current_time + step['delay']
                await self._schedule_step(
                    step,
                    lead_data,
                    deal['id'],
                    execution_time
                )

            return deal['id']

        except Exception as e:
            self.logger.error(f"Error initiating nurture sequence: {str(e)}")
            raise

    async def _schedule_step(
        self,
        step: Dict,
        lead_data: Dict,
        deal_id: int,
        execution_time: datetime
    ):
        """
        Schedule a nurture sequence step.
        """
        # Create Pipedrive activity for tracking
        activity_subject = f"Nurture Step: {step['type']}"
        await self.pipedrive.create_activity(
            deal_id=deal_id,
            activity_type=step['type'],
            subject=activity_subject,
            due_date=execution_time
        )

        # Generate content for the step
        content = await self._generate_step_content(
            step['template'],
            lead_data
        )

        # Schedule content delivery
        if step['type'] in ['personalized_content', 'case_study', 'educational_content']:
            await self.social_poster.schedule_posts(
                content={'linkedin': [content]},
                platforms=['linkedin'],
                schedule_times=[execution_time]
            )

        # Add note to deal
        await self.pipedrive.add_note(
            deal_id=deal_id,
            content=f"Scheduled {step['type']} for {execution_time}"
        )

    async def _generate_step_content(
        self,
        template: str,
        lead_data: Dict
    ) -> str:
        """
        Generate personalized content for nurture step.
        """
        # Use content generator to create personalized content
        content = await self.content_generator.create_industry_posts(
            industry=lead_data['industry'],
            custom_pain_points=[],
            value_prop="30% cost reduction",
            platforms=['linkedin'],
            post_count=1
        )
        
        return content['linkedin'][0]

    async def handle_sequence_response(
        self,
        deal_id: int,
        response_type: str,
        response_content: str
    ):
        """
        Handle responses during nurture sequence.
        """
        try:
            # Add response to Pipedrive
            await self.pipedrive.add_note(
                deal_id=deal_id,
                content=f"Sequence Response ({response_type}): {response_content}"
            )

            # Adjust sequence based on response
            if response_type == 'positive':
                # Create task for SDR follow-up
                await self.pipedrive.create_activity(
                    deal_id=deal_id,
                    activity_type='follow_up',
                    subject='Positive Sequence Response - Priority Follow-up',
                    due_date=datetime.now() + timedelta(hours=24)
                )
            elif response_type == 'negative':
                # Pause sequence and create task for review
                await self.pipedrive.create_activity(
                    deal_id=deal_id,
                    activity_type='review',
                    subject='Review Negative Sequence Response',
                    due_date=datetime.now() + timedelta(days=2)
                )

        except Exception as e:
            self.logger.error(f"Error handling sequence response: {str(e)}")
            raise