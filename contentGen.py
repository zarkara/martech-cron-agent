import openai
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import logging

class GPTContentGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the content generator with OpenAI credentials and configuration.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        # Industry-specific templates and configurations
        self.industry_templates = {
            'retail': {
                'pain_points': [
                    'High transaction fees eating into margins',
                    'Complex pricing structures',
                    'Long settlement times',
                    'Integration difficulties with POS systems'
                ],
                'tone': 'professional yet approachable',
                'content_length': {'linkedin': 1200, 'twitter': 280}
            },
            'hospitality': {
                'pain_points': [
                    'Customer card decline rates',
                    'International payment processing fees',
                    'Integration with booking systems',
                    'Seasonal cash flow management'
                ],
                'tone': 'friendly and solution-focused',
                'content_length': {'linkedin': 1000, 'twitter': 280}
            }
            # Add more industries as needed
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def create_industry_posts(
        self,
        industry: str,
        custom_pain_points: Optional[List[str]] = None,
        value_prop: str = "30% cost reduction",
        platforms: List[str] = ['linkedin', 'twitter'],
        post_count: int = 5
    ) -> Dict[str, List[str]]:
        """
        Generate industry-specific social media posts.
        
        Args:
            industry: Target industry
            custom_pain_points: Additional pain points to consider
            value_prop: Main value proposition
            platforms: Target social media platforms
            post_count: Number of posts to generate per platform
            
        Returns:
            Dictionary of platform-specific posts
        """
        try:
            template = self.industry_templates.get(industry.lower())
            if not template:
                raise ValueError(f"No template found for industry: {industry}")
            
            # Combine default and custom pain points
            all_pain_points = template['pain_points']
            if custom_pain_points:
                all_pain_points.extend(custom_pain_points)
            
            generated_content = {}
            
            for platform in platforms:
                posts = await self._generate_platform_specific_content(
                    industry=industry,
                    platform=platform,
                    pain_points=all_pain_points,
                    value_prop=value_prop,
                    template=template,
                    count=post_count
                )
                generated_content[platform] = posts
                
            return generated_content
            
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise

    async def _generate_platform_specific_content(
        self,
        industry: str,
        platform: str,
        pain_points: List[str],
        value_prop: str,
        template: Dict,
        count: int
    ) -> List[str]:
        """
        Generate platform-specific content using GPT.
        """
        max_length = template['content_length'][platform]
        tone = template['tone']
        
        prompt = self._create_platform_prompt(
            industry=industry,
            platform=platform,
            pain_points=pain_points,
            value_prop=value_prop,
            tone=tone,
            max_length=max_length
        )
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert B2B payment processing copywriter."},
                    {"role": "user", "content": prompt}
                ],
                n=count,
                temperature=0.7,
                max_tokens=max_length
            )
            
            posts = [choice.message.content for choice in response.choices]
            return self._post_process_content(posts, platform)
            
        except Exception as e:
            self.logger.error(f"Error generating content for {platform}: {str(e)}")
            raise

    def _create_platform_prompt(
        self,
        industry: str,
        platform: str,
        pain_points: List[str],
        value_prop: str,
        tone: str,
        max_length: int
    ) -> str:
        """
        Create platform-specific prompt for GPT.
        """
        prompt = f"""
        Create a {platform} post for {industry} businesses about payment processing solutions.
        
        Key points to include:
        - Main value proposition: {value_prop}
        - Address these pain points: {', '.join(pain_points)}
        
        Requirements:
        - Use a {tone} tone
        - Maximum length: {max_length} characters
        - Include relevant hashtags for {platform}
        - Focus on ROI and cost savings
        - Include a clear call to action
        
        The post should be engaging, professional, and highlight the cost-saving benefits
        while addressing specific industry pain points.
        """
        return prompt

    def _post_process_content(self, posts: List[str], platform: str) -> List[str]:
        """
        Post-process generated content for platform-specific requirements.
        """
        processed_posts = []
        for post in posts:
            # Remove extra whitespace and normalize line breaks
            processed = ' '.join(post.split())
            
            # Platform-specific processing
            if platform == 'twitter':
                # Ensure posts don't exceed Twitter's character limit
                if len(processed) > 280:
                    processed = processed[:277] + "..."
                    
            # Add tracking parameters if needed
            processed = self._add_tracking_parameters(processed, platform)
            
            processed_posts.append(processed)
            
        return processed_posts

    def _add_tracking_parameters(self, post: str, platform: str) -> str:
        """
        Add UTM parameters or other tracking elements to posts.
        """
        # Add UTM parameters to any links in the post
        if "http" in post:
            utm_params = f"?utm_source={platform}&utm_medium=social&utm_campaign=payment_processing"
            # Simple URL replacement - in production, use proper URL parsing
            post = post.replace("http", f"http{utm_params}")
        
        return post

    async def generate_weekly_content_calendar(
        self,
        industry: str,
        start_date: datetime,
        posts_per_day: int = 2
    ) -> Dict:
        """
        Generate a week's worth of content calendar.
        """
        # Implementation for content calendar generation
        # This would schedule posts across the week based on optimal posting times
        pass

    async def analyze_content_performance(
        self,
        previous_posts: List[Dict],
        metrics: List[str]
    ) -> Dict:
        """
        Analyze performance of previous posts to optimize future content.
        """
        # Implementation for content performance analysis
        # This would help optimize future content based on engagement metrics
        pass