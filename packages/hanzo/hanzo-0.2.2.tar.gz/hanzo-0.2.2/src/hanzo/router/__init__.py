"""Router module - re-exports from hanzo-router package."""

try:
    # Import all exports from hanzo-router (which internally uses 'router' package name)
    from router import *
    from router import Router, completion, acompletion, embedding, aembedding
    
    # Ensure these are explicitly available
    __all__ = ["Router", "completion", "acompletion", "embedding", "aembedding"]
except ImportError as e:
    # If hanzo-router is not installed, provide helpful error
    import sys
    print(f"Error importing router: {e}", file=sys.stderr)
    print("Please install hanzo-router: pip install hanzo[router] or pip install hanzo[all]", file=sys.stderr)
    
    # Define placeholders to avoid complete failure
    Router = None
    completion = None
    acompletion = None
    embedding = None
    aembedding = None