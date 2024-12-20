generator = GPTContentGenerator(api_key="your-openai-api-key")

# Generate content
async def generate_campaign_content():
    posts = await generator.create_industry_posts(
        industry="retail",
        custom_pain_points=[
            "Outdated payment hardware",
            "Chargeback disputes"
        ],
        value_prop="30% reduction in processing fees",
        platforms=['linkedin', 'twitter'],
        post_count=5
    )
    return posts

async def run_lead_generation_campaign():
    # Initialize components
    linkedin_api = LinkedInAPI(
        client_id="your_id",
        client_secret="your_secret",
        refresh_token="your_token"
    )
    
    social_poster = SocialMediaPoster(
        linkedin_credentials={...},
        twitter_credentials={...}
    )
    
    lead_router = LeadRouter(
        crm_client=your_crm_client,
        sdr_email="sdr@titanium-payments.com"
    )
    
    # Generate prospects
    prospects = await linkedin_api.get_targeted_companies(
        industry_filters=['retail', 'hospitality'],
        company_size='50-1000',
        location=['US']
    )
    
    # Create and post content
    responses = await social_poster.schedule_posts(
        content=your_content,
        platforms=['linkedin', 'twitter'],
        monitoring=True
    )
    
    # Process leads
    qualified_leads = await lead_router.process_responses(
        responses=responses,
        qualification_criteria={
            'minimum_score': 0.7,
            'interest_level': 'high',
            'decision_maker': True
        }
    )