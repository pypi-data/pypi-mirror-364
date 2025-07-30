"""
ScoutML - Scout ML Research Papers

A powerful command-line interface and Python library for discovering, analyzing, and implementing ML research.
"""

__version__ = "0.1.2"
__author__ = "ProspectML"
__email__ = "info@prospectml.com"

from .client import ScoutMLClient
from .config import Config
from .exceptions import (
    ScoutMLError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError
)

# Convenience functions for common operations
_default_client = None

def _get_client():
    """Get or create default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = ScoutMLClient()
    return _default_client

# Search functions
def search(query, limit=20, **kwargs):
    """
    Search for papers using natural language query.
    
    Args:
        query (str): Search query
        limit (int): Number of results (default: 20)
        **kwargs: Additional filters (year_min, year_max, min_citations, venue, sota_only, domain)
    
    Returns:
        dict: Search results with papers
        
    Example:
        >>> import scoutml
        >>> results = scoutml.search("vision transformers", limit=5, year_min=2021)
        >>> for paper in results['papers']:
        ...     print(f"{paper['title']} ({paper['year']}) - {paper['citations']} citations")
    """
    client = _get_client()
    return client.semantic_search(query, limit=limit, **kwargs)

def method_search(method, limit=20, sort_by="citations", **kwargs):
    """
    Search papers using a specific method.
    
    Args:
        method (str): Method/technique name
        limit (int): Number of results
        sort_by (str): Sort by 'citations', 'year', or 'novelty'
        **kwargs: Additional filters (year_min, year_max)
    
    Returns:
        dict: Papers using the method
    """
    client = _get_client()
    return client.method_search(method, limit=limit, sort_by=sort_by, **kwargs)

def dataset_search(dataset, limit=20, include_benchmarks=True, **kwargs):
    """
    Search papers using a specific dataset.
    
    Args:
        dataset (str): Dataset name
        limit (int): Number of results
        include_benchmarks (bool): Include benchmark results
        **kwargs: Additional filters (year_min, year_max)
    
    Returns:
        dict: Papers using the dataset
    """
    client = _get_client()
    return client.dataset_search(dataset, limit=limit, include_benchmarks=include_benchmarks, **kwargs)

# Paper analysis functions
def get_paper(arxiv_id, include_similar=False, similar_limit=5):
    """
    Get detailed information about a paper.
    
    Args:
        arxiv_id (str): ArXiv paper ID
        include_similar (bool): Include similar papers
        similar_limit (int): Number of similar papers
    
    Returns:
        dict: Paper details
        
    Example:
        >>> paper = scoutml.get_paper("2103.00020", include_similar=True)
        >>> print(paper['paper']['title'])
        >>> print(paper['paper']['abstract'])
    """
    client = _get_client()
    return client.get_paper(arxiv_id, include_similar=include_similar, similar_limit=similar_limit)

def compare_papers(*paper_ids):
    """
    Compare multiple papers.
    
    Args:
        *paper_ids: ArXiv IDs of papers to compare (2-10 papers)
    
    Returns:
        dict: Comparative analysis
        
    Example:
        >>> comparison = scoutml.compare_papers("1810.04805", "2005.14165", "1910.10683")
        >>> print(comparison['analysis']['key_differences'])
    """
    client = _get_client()
    return client.compare_papers(list(paper_ids))

def find_similar_papers(paper_id=None, abstract_text=None, limit=10, threshold=0.7):
    """
    Find papers similar to a given paper or abstract.
    
    Args:
        paper_id (str, optional): ArXiv ID of reference paper
        abstract_text (str, optional): Abstract text to match
        limit (int): Number of results
        threshold (float): Similarity threshold (0-1)
    
    Returns:
        dict: Similar papers with similarity scores
    """
    client = _get_client()
    return client.find_similar_papers(
        paper_id=paper_id, 
        abstract_text=abstract_text, 
        limit=limit, 
        similarity_threshold=threshold
    )

# Research synthesis
def generate_review(topic, year_min=None, year_max=None, min_citations=0, limit=50):
    """
    Generate a literature review on a topic.
    
    Args:
        topic (str): Research topic
        year_min (int, optional): Minimum year
        year_max (int, optional): Maximum year
        min_citations (int): Minimum citation count
        limit (int): Number of papers to analyze
    
    Returns:
        dict: Literature review with analysis
    """
    client = _get_client()
    return client.generate_literature_review(
        topic, year_min=year_min, year_max=year_max, 
        min_citations=min_citations, limit=limit
    )

# Insights functions
def get_reproducible_papers(domain=None, year_min=None, year_max=None, limit=20):
    """
    Get papers ranked by reproducibility.
    
    Args:
        domain (str, optional): Filter by domain
        year_min (int, optional): Minimum year
        year_max (int, optional): Maximum year
        limit (int): Number of results
    
    Returns:
        dict: Papers with reproducibility scores
    """
    client = _get_client()
    return client.get_reproducibility_ranked(
        domain=domain, year_min=year_min, year_max=year_max, limit=limit
    )

def analyze_compute_trends(method=None, year_min=None, year_max=None):
    """
    Analyze compute requirements and trends.
    
    Args:
        method (str, optional): Filter by method
        year_min (int, optional): Minimum year
        year_max (int, optional): Maximum year
    
    Returns:
        dict: Compute analysis and trends
    """
    client = _get_client()
    return client.analyze_compute_requirements(
        method=method, year_min=year_min, year_max=year_max
    )

def analyze_funding(institution=None, source=None, year_min=None, year_max=None, limit=20):
    """
    Analyze funding sources and impact.
    
    Args:
        institution (str, optional): Filter by institution
        source (str, optional): Filter by funding source
        year_min (int, optional): Minimum year
        year_max (int, optional): Maximum year
        limit (int): Number of top sources
    
    Returns:
        dict: Funding analysis
    """
    client = _get_client()
    return client.analyze_funding(
        institution=institution, funding_source=source,
        year_min=year_min, year_max=year_max, limit=limit
    )

# Agent functions
def get_implementation_guide(arxiv_id, framework="pytorch", level="intermediate"):
    """
    Get implementation guide for a paper.
    
    Args:
        arxiv_id (str): ArXiv paper ID
        framework (str): Target framework ('pytorch', 'tensorflow', 'jax', 'other')
        level (str): Experience level ('beginner', 'intermediate', 'advanced')
    
    Returns:
        dict: Implementation guide
        
    Example:
        >>> guide = scoutml.get_implementation_guide("2010.11929", framework="pytorch")
        >>> print(guide['implementation']['overview'])
    """
    client = _get_client()
    return client.implement_guide(arxiv_id, target_framework=framework, experience_level=level)

def critique_paper(arxiv_id, aspects=None):
    """
    Get comprehensive critique of a paper.
    
    Args:
        arxiv_id (str): ArXiv paper ID
        aspects (list, optional): Aspects to critique ['methodology', 'experiments', 'claims', 'reproducibility']
    
    Returns:
        dict: Research critique
    """
    client = _get_client()
    return client.research_critique(arxiv_id, critique_aspects=aspects)

def solve_limitations(arxiv_id, focus=None, tradeoffs=None):
    """
    Get solutions for paper limitations.
    
    Args:
        arxiv_id (str): ArXiv paper ID
        focus (str, optional): Specific limitation to focus on
        tradeoffs (list, optional): Acceptable tradeoffs
    
    Returns:
        dict: Solutions and workarounds
    """
    client = _get_client()
    return client.solve_limitations(arxiv_id, focus_limitation=focus, acceptable_tradeoffs=tradeoffs)

def design_experiment(base_paper, hypothesis, gpu_hours=None, datasets=None):
    """
    Design experiment to test hypothesis.
    
    Args:
        base_paper (str): ArXiv ID of base paper
        hypothesis (str): Hypothesis to test
        gpu_hours (int, optional): Available GPU hours
        datasets (list, optional): Available datasets
    
    Returns:
        dict: Experiment design
    """
    client = _get_client()
    resources = {}
    if gpu_hours:
        resources['gpu_hours'] = gpu_hours
    if datasets:
        resources['datasets'] = datasets
    return client.design_experiment(base_paper, hypothesis, resources=resources)

# Direct client access for advanced usage
def get_client(config=None):
    """
    Get a ScoutML client instance.
    
    Args:
        config (Config, optional): Custom configuration
    
    Returns:
        ScoutMLClient: Client instance for advanced usage
        
    Example:
        >>> client = scoutml.get_client()
        >>> # Use client methods directly
        >>> results = client.semantic_search("transformers", limit=100)
    """
    if config:
        return ScoutMLClient(config)
    return _get_client()

# Convenience class for context manager usage
class Scout:
    """
    Context manager for ScoutML operations.
    
    Example:
        >>> with scoutml.Scout() as scout:
        ...     papers = scout.search("bert variants", limit=5)
        ...     comparison = scout.compare_papers(papers['papers'][0]['arxiv_id'], 
        ...                                      papers['papers'][1]['arxiv_id'])
    """
    def __init__(self, config=None):
        self.client = ScoutMLClient(config)
    
    def __enter__(self):
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close session if needed
        if hasattr(self.client, 'session'):
            self.client.session.close()
        return False

__all__ = [
    # Core classes
    'ScoutMLClient',
    'Config',
    'Scout',
    
    # Exceptions
    'ScoutMLError',
    'AuthenticationError',
    'NotFoundError',
    'RateLimitError',
    'ServerError',
    
    # Search functions
    'search',
    'method_search',
    'dataset_search',
    
    # Analysis functions
    'get_paper',
    'compare_papers',
    'find_similar_papers',
    
    # Synthesis
    'generate_review',
    
    # Insights
    'get_reproducible_papers',
    'analyze_compute_trends',
    'analyze_funding',
    
    # Agent functions
    'get_implementation_guide',
    'critique_paper',
    'solve_limitations',
    'design_experiment',
    
    # Utility
    'get_client',
]