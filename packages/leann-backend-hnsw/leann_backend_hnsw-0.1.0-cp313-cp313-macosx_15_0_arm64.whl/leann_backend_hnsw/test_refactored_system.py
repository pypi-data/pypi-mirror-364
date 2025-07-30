#!/usr/bin/env python3
"""
Test script to verify the refactored embedding system works correctly.
"""

import sys
import os
from pathlib import Path
import numpy as np

# Add leann-core to path
current_dir = Path(__file__).parent
leann_core_path = current_dir.parent.parent / "leann-core" / "src"
sys.path.insert(0, str(leann_core_path))

def test_embedding_compute_direct():
    """Test the unified embedding compute module directly"""
    print("🔧 Testing unified embedding compute module...")
    
    from leann.embedding_compute import compute_embeddings_sentence_transformers
    
    test_texts = [
        "This is a test sentence.",
        "Another test for embeddings.",
        "Testing the refactored system."
    ]
    
    # Test with different models
    models_to_test = [
        "sentence-transformers/all-mpnet-base-v2",
        "Qwen/Qwen3-Embedding-0.6B"
    ]
    
    for model_name in models_to_test:
        print(f"\n📝 Testing model: {model_name}")
        try:
            embeddings = compute_embeddings_sentence_transformers(
                test_texts, 
                model_name, 
                use_fp16=True
            )
            
            print(f"✅ Success! Shape: {embeddings.shape}")
            print(f"   Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
            
            # Check normalization
            norms = np.linalg.norm(embeddings, axis=1)
            if np.allclose(norms, 1.0, rtol=1e-3):
                print("✅ Embeddings are properly normalized")
            else:
                print(f"❌ Embeddings not normalized! Norms: {norms}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")

def test_embedding_server():
    """Test the simplified embedding server"""
    print("\n🖥️ Testing simplified embedding server...")
    
    # Import the server
    from hnsw_embedding_server import create_hnsw_embedding_server
    import threading
    import time
    import zmq
    import msgpack
    
    # Test data
    test_data = {
        "1": "This is test passage 1",
        "2": "This is test passage 2", 
        "3": "This is test passage 3"
    }
    
    # Start server in background thread
    def run_server():
        create_hnsw_embedding_server(
            passages_data=test_data,
            zmq_port=5558,  # Use different port to avoid conflicts
            model_name="sentence-transformers/all-mpnet-base-v2",
            embedding_mode="sentence-transformers",
            use_fp16=True
        )
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(3)
    
    # Test client requests
    try:
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5558")
        socket.setsockopt(zmq.RCVTIMEO, 10000)  # 10 second timeout
        
        # Test 1: Query model
        print("📋 Testing model query...")
        socket.send(msgpack.packb(["__QUERY_MODEL__"]))
        response = msgpack.unpackb(socket.recv())
        print(f"✅ Model: {response[0]}")
        
        # Test 2: Direct text embedding
        print("📋 Testing direct text embedding...")
        test_texts = ["This is a test", "Another test"]
        socket.send(msgpack.packb(test_texts))
        response = msgpack.unpackb(socket.recv())
        embeddings = np.array(response)
        print(f"✅ Direct embedding shape: {embeddings.shape}")
        print(f"   Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
        
        # Test 3: Passage ID lookup
        print("📋 Testing passage ID lookup...")
        socket.send(msgpack.packb([["1", "2"]]))
        response = msgpack.unpackb(socket.recv())
        shape = response[0]
        flat_embeddings = response[1]
        embeddings = np.array(flat_embeddings).reshape(shape)
        print(f"✅ Passage lookup shape: {embeddings.shape}")
        print(f"   Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
        
        socket.close()
        context.term()
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")

def test_api_integration():
    """Test the API integration with new compute module"""
    print("\n🔗 Testing API integration...")
    
    try:
        # Test direct computation through API
        from leann.api import compute_embeddings
        
        test_texts = ["Test sentence 1", "Test sentence 2"]
        
        embeddings = compute_embeddings(
            test_texts,
            "sentence-transformers/all-mpnet-base-v2", 
            mode="sentence-transformers",
            use_server=False
        )
        
        print(f"✅ API direct computation shape: {embeddings.shape}")
        print(f"   Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing refactored embedding system...\n")
    
    # Test direct compute module
    test_embedding_compute_direct()
    
    # Test API integration  
    test_api_integration()
    
    # Test embedding server
    test_embedding_server()
    
    print("\n✅ All tests completed!")