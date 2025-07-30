"""Unit tests for ScoutML library interface."""

import pytest
from unittest.mock import Mock, patch
import scoutml


class TestLibraryInterface:
    """Test the public library interface."""
    
    @patch('scoutml.ScoutMLClient')
    def test_search_function(self, mock_client_class):
        """Test the search convenience function."""
        # Mock client instance
        mock_client = Mock()
        mock_client.semantic_search.return_value = {"papers": []}
        mock_client_class.return_value = mock_client
        
        # Test search
        result = scoutml.search("test query", limit=10)
        
        # Verify client was called correctly
        mock_client.semantic_search.assert_called_once_with(
            "test query", limit=10
        )
        assert result == {"papers": []}
    
    def test_get_paper_function(self):
        """Test the get_paper convenience function."""
        # Reset the default client to ensure fresh mock
        scoutml._default_client = None
        
        with patch('scoutml.ScoutMLClient') as mock_client_class:
            mock_client = Mock()
            mock_client.get_paper.return_value = {"paper": {"title": "Test"}}
            mock_client_class.return_value = mock_client
            
            result = scoutml.get_paper("1234", include_similar=True)
            
            mock_client.get_paper.assert_called_once_with(
                "1234", include_similar=True, similar_limit=5
            )
            assert result == {"paper": {"title": "Test"}}
    
    def test_compare_papers_function(self):
        """Test the compare_papers convenience function."""
        # Reset the default client to ensure fresh mock
        scoutml._default_client = None
        
        with patch('scoutml.ScoutMLClient') as mock_client_class:
            mock_client = Mock()
            mock_client.compare_papers.return_value = {"analysis": {}}
            mock_client_class.return_value = mock_client
            
            result = scoutml.compare_papers("1234", "5678", "9012")
            
            mock_client.compare_papers.assert_called_once_with(
                ["1234", "5678", "9012"]
            )
            assert result == {"analysis": {}}
    
    def test_scout_context_manager(self):
        """Test Scout context manager."""
        with scoutml.Scout() as scout:
            assert hasattr(scout, 'semantic_search')
            assert hasattr(scout, 'get_paper')
            assert hasattr(scout, 'compare_papers')
    
    def test_get_client_function(self):
        """Test get_client function."""
        # Reset the default client
        scoutml._default_client = None
        
        # Test default client creation
        client = scoutml.get_client()
        assert isinstance(client, scoutml.ScoutMLClient)
        
        # Test with custom config
        custom_config = scoutml.Config()
        custom_config.api_key = "custom-key"
        custom_client = scoutml.get_client(custom_config)
        assert isinstance(custom_client, scoutml.ScoutMLClient)
        assert custom_client.config.api_key == "custom-key"
    
    def test_all_exports(self):
        """Test that all expected functions are exported."""
        expected_exports = [
            # Core classes
            'ScoutMLClient', 'Config', 'Scout',
            # Exceptions
            'ScoutMLError', 'AuthenticationError', 'NotFoundError',
            'RateLimitError', 'ServerError',
            # Search functions
            'search', 'method_search', 'dataset_search',
            # Analysis functions
            'get_paper', 'compare_papers', 'find_similar_papers',
            # Synthesis
            'generate_review',
            # Insights
            'get_reproducible_papers', 'analyze_compute_trends', 'analyze_funding',
            # Agent functions
            'get_implementation_guide', 'critique_paper', 
            'solve_limitations', 'design_experiment',
            # Utility
            'get_client',
        ]
        
        for export in expected_exports:
            assert hasattr(scoutml, export), f"Missing export: {export}"