"""Unit tests for ScoutML client."""

import pytest
from unittest.mock import Mock, patch
from scoutml import ScoutMLClient, Config
from scoutml.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError
)


class TestScoutMLClient:
    """Test ScoutML client functionality."""
    
    def setup_method(self):
        """Set up test client."""
        self.config = Config()
        self.config.api_key = "test-api-key"
        self.client = ScoutMLClient(self.config)
    
    @patch('requests.Session.request')
    def test_semantic_search(self, mock_request):
        """Test semantic search functionality."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "papers": [
                {
                    "arxiv_id": "2103.00020",
                    "title": "Learning Transferable Visual Models",
                    "year": 2021,
                    "citations": 5000
                }
            ]
        }
        mock_request.return_value = mock_response
        
        # Test search
        result = self.client.semantic_search("vision transformers", limit=5)
        
        assert "papers" in result
        assert len(result["papers"]) == 1
        assert result["papers"][0]["arxiv_id"] == "2103.00020"
    
    @patch('requests.Session.request')
    def test_get_paper(self, mock_request):
        """Test get paper functionality."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "paper": {
                "arxiv_id": "2103.00020",
                "title": "CLIP",
                "abstract": "Test abstract"
            }
        }
        mock_request.return_value = mock_response
        
        # Test get paper
        result = self.client.get_paper("2103.00020")
        
        assert "paper" in result
        assert result["paper"]["arxiv_id"] == "2103.00020"
    
    @patch('requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with pytest.raises(AuthenticationError):
            self.client.semantic_search("test")
    
    @patch('requests.Session.request')
    def test_not_found_error(self, mock_request):
        """Test not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        with pytest.raises(NotFoundError):
            self.client.get_paper("invalid-id")
    
    @patch('requests.Session.request')
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            self.client.semantic_search("test")
    
    @patch('requests.Session.request')
    def test_server_error(self, mock_request):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response
        
        with pytest.raises(ServerError):
            self.client.semantic_search("test")
    
    def test_compare_papers_validation(self):
        """Test compare papers validation."""
        # Too few papers
        with pytest.raises(ValueError, match="At least 2 paper IDs required"):
            self.client.compare_papers(["1234"])
        
        # Too many papers
        with pytest.raises(ValueError, match="Maximum 10 papers"):
            self.client.compare_papers(["1234"] * 11)
    
    def test_find_similar_papers_validation(self):
        """Test find similar papers validation."""
        # No input provided
        with pytest.raises(ValueError, match="Either paper_id or abstract_text must be provided"):
            self.client.find_similar_papers()
        
        # Both inputs provided
        with pytest.raises(ValueError, match="Provide either paper_id or abstract_text, not both"):
            self.client.find_similar_papers(paper_id="1234", abstract_text="test")