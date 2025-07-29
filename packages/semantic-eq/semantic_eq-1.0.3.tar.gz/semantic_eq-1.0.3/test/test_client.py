"""
Tests for the Semantic EQ SDK client
"""

import pytest
import json
from unittest.mock import Mock, patch
from semantic_eq_sdk import SemanticEQClient, OptimizationConfig, OptimizationError


class TestSemanticEQClient:
    """Test cases for SemanticEQClient"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = SemanticEQClient(
            base_url="http://localhost:8001",
            api_key="test-api-key"
        )
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.base_url == "http://localhost:8001"
        assert self.client.api_key == "test-api-key"
        assert "Authorization" in self.client.session.headers
        assert self.client.session.headers["Authorization"] == "Bearer test-api-key"
    
    def test_client_initialization_without_api_key(self):
        """Test client initialization without API key"""
        client = SemanticEQClient(base_url="http://localhost:8001")
        assert "Authorization" not in client.session.headers
    
    @patch('requests.Session.post')
    def test_optimize_prompt_success(self, mock_post):
        """Test successful prompt optimization"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "original_prompt": "Write a subject line",
            "optimized_prompts": [
                {
                    "text": "Create an engaging email subject",
                    "metrics": {
                        "semantic_similarity": 0.95,
                        "coherence_score": 0.9,
                        "fluency_score": 0.85,
                        "diversity_score": 0.7,
                        "compression_ratio": 0.8
                    },
                    "optimization_type": "clarity_enhancement",
                    "confidence_score": 0.92
                }
            ],
            "best_prompt": {
                "text": "Create an engaging email subject",
                "metrics": {
                    "semantic_similarity": 0.95,
                    "coherence_score": 0.9,
                    "fluency_score": 0.85,
                    "diversity_score": 0.7,
                    "compression_ratio": 0.8
                },
                "optimization_type": "clarity_enhancement",
                "confidence_score": 0.92
            },
            "optimization_id": "opt_123",
            "processing_time": 1.5,
            "metadata": {}
        }
        mock_post.return_value = mock_response
        
        # Test optimization
        result = self.client.optimize_prompt(
            prompt="Write a subject line",
            config=OptimizationConfig(num_variants=1)
        )
        
        # Assertions
        assert result.original_prompt == "Write a subject line"
        assert result.best_prompt.text == "Create an engaging email subject"
        assert result.best_prompt.metrics.semantic_similarity == 0.95
        assert result.optimization_id == "opt_123"
        assert len(result.optimized_prompts) == 1
    
    @patch('requests.Session.post')
    def test_optimize_prompt_api_error(self, mock_post):
        """Test API error handling"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid prompt"}
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        # Test error handling
        with pytest.raises(OptimizationError, match="Invalid request"):
            self.client.optimize_prompt("Invalid prompt")
    
    @patch('requests.Session.post')
    def test_batch_optimization_success(self, mock_post):
        """Test successful batch optimization"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "results": [
                {
                    "original_prompt": "Prompt 1",
                    "optimized_prompts": [
                        {
                            "text": "Optimized prompt 1",
                            "metrics": {
                                "semantic_similarity": 0.9,
                                "coherence_score": 0.85,
                                "fluency_score": 0.8,
                                "diversity_score": 0.6
                            },
                            "optimization_type": "clarity",
                            "confidence_score": 0.88
                        }
                    ],
                    "best_prompt": {
                        "text": "Optimized prompt 1",
                        "metrics": {
                            "semantic_similarity": 0.9,
                            "coherence_score": 0.85,
                            "fluency_score": 0.8,
                            "diversity_score": 0.6
                        },
                        "optimization_type": "clarity",
                        "confidence_score": 0.88
                    },
                    "optimization_id": "batch_opt_1",
                    "processing_time": 1.2,
                    "metadata": {}
                }
            ],
            "failed_prompts": [],
            "batch_id": "batch_123",
            "total_processed": 1,
            "processing_time": 1.2,
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_post.return_value = mock_response
        
        # Test batch optimization
        result = self.client.optimize_prompts_batch(
            prompts=["Prompt 1"],
            config=OptimizationConfig(num_variants=1)
        )
        
        # Assertions
        assert result.success is True
        assert len(result.results) == 1
        assert result.results[0].original_prompt == "Prompt 1"
        assert result.batch_id == "batch_123"
        assert result.total_processed == 1
    
    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_get.return_value = mock_response
        
        # Test health check
        result = self.client.health_check()
        
        # Assertions
        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"
    
    @patch('requests.Session.get')
    def test_get_optimization_status(self, mock_get):
        """Test getting optimization status"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "opt_123",
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "completed_at": "2024-01-01T12:01:30Z"
        }
        mock_get.return_value = mock_response
        
        # Test status check
        result = self.client.get_optimization_status("opt_123")
        
        # Assertions
        assert result["status"] == "completed"
        assert result["id"] == "opt_123"
    
    def test_serialization_methods(self):
        """Test request serialization methods"""
        from semantic_eq_sdk.models import OptimizationRequest
        
        # Create test request
        config = OptimizationConfig(
            model_name="gpt-4",
            num_variants=3,
            constraints=["keep_short"]
        )
        
        request = OptimizationRequest(
            prompt="Test prompt",
            config=config,
            context="Test context"
        )
        
        # Test serialization
        serialized = self.client._serialize_optimization_request(request)
        
        # Assertions
        assert serialized["prompt"] == "Test prompt"
        assert serialized["config"]["model_name"] == "gpt-4"
        assert serialized["config"]["num_variants"] == 3
        assert serialized["config"]["constraints"] == ["keep_short"]
        assert serialized["context"] == "Test context"


if __name__ == "__main__":
    pytest.main([__file__])