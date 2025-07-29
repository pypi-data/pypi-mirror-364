"""
Semantic EQ API Client

This module provides a client for optimizing prompts using the Semantic EQ API.
"""

import json
import requests
from typing import Optional, Dict, Any
from .models import OptimizationResult


class SemanticEQError(Exception):
    """Base exception for Semantic EQ SDK errors"""
    pass


class OptimizationError(SemanticEQError):
    """Raised when prompt optimization fails"""
    pass


class SemanticEQ:
    """Client for optimizing prompts using the Semantic EQ API"""

    def __init__(self, api_key: str, base_url: str = "https://semantic-eq-backend-lq2c35zaaa-uc.a.run.app"):
        """
        Initialize the Semantic EQ Client
        
        Args:
            api_key: API key for authentication (required)
            base_url: Base URL of the Semantic EQ API (e.g., 'https://api.semantic-eq.com')
        """
        if not api_key:
            raise ValueError("API key is required. Get your API key from https://semantic-eq.com")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up authentication headers
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'semantic-eq-sdk/1.0.1'
        })

    def optimize_prompt(self, prompt: str) -> OptimizationResult:
        """
        Optimize a single prompt for semantic equivalence
        
        Args:
            prompt: The prompt text to optimize
            
        Returns:
            OptimizationResult: The optimization result with original and optimized prompt
            
        Raises:
            OptimizationError: If the optimization fails
        """
        try:
            # Make the API request
            url = f"{self.base_url}/optimize"
            payload = {"prompt": prompt}
            
            response = self.session.post(url, json=payload)
            
            # Handle different response codes
            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise OptimizationError(f"Invalid request: {error_data.get('error', response.text)}")
            elif response.status_code == 401:
                raise OptimizationError("Authentication failed - check your API key")
            elif response.status_code == 429:
                raise OptimizationError("Rate limit exceeded - please try again later")
            elif response.status_code != 200:
                raise OptimizationError(f"API request failed with status {response.status_code}: {response.text}")
            
            # Parse the response
            data = response.json()
            
            return OptimizationResult(
                original_prompt=data['original_prompt'],
                optimized_prompt=data['optimized_prompt'],
                improvement_score=data.get('improvement_score')
            )
            
        except requests.RequestException as e:
            raise OptimizationError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise OptimizationError(f"Invalid JSON response: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Dict containing health status information
            
        Raises:
            SemanticEQError: If health check fails
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise SemanticEQError(f"Health check failed with status {response.status_code}")
                
        except requests.RequestException as e:
            raise SemanticEQError(f"Health check network error: {str(e)}")