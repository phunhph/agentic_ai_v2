import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.getcwd())
load_dotenv()

from core.graph.builder import graph
from core.agents.learning_agent import find_semantic_cache

def test_graph_build():
    try:
        print("[SUCCESS] Graph built successfully.")
        print(f"Nodes: {list(graph.nodes.keys())}")
    except Exception as e:
        print(f"[ERROR] Graph build failed: {e}")

def test_semantic_cache():
    try:
        # Test with a dummy query
        result = find_semantic_cache("Show me all accounts", threshold=0.1)
        print(f"[SUCCESS] Semantic cache call successful. Result: {result}")
    except Exception as e:
        print(f"[ERROR] Semantic cache call failed: {e}")

if __name__ == "__main__":
    test_graph_build()
    test_semantic_cache()
