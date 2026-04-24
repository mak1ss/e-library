#!/usr/bin/env python3
"""
Test Script: Sentence Transformer Integration (Task 1.9)
Purpose: Verify sentence-transformers model loading, embedding generation, 
latency, and memory usage before production integration.

Run: python test_sentence_transformer.py
"""

import sys
import time
import tracemalloc
from pathlib import Path

# Add recommenderService to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def get_current_memory_mb():
    """Get current memory usage in MB using tracemalloc"""
    current, peak = tracemalloc.get_traced_memory()
    return current / 1024 / 1024, peak / 1024 / 1024


def test_sentence_transformer():
    """Test sentence-transformers integration"""
    
    # Start memory tracing
    tracemalloc.start()
    
    print("=" * 70)
    print("SENTENCE TRANSFORMER INTEGRATION TEST (Task 1.9)")
    print("=" * 70)
    print()
    
    # Test 1: Import SentenceTransformer
    print("[1/7] Testing import of SentenceTransformer...")
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ Successfully imported SentenceTransformer")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    print()
    
    # Test 2: Memory baseline
    print("[2/7] Recording baseline memory usage...")
    memory_before, _ = get_current_memory_mb()
    print(f"✓ Baseline memory: {memory_before:.2f} MB")
    print()
    
    # Test 3: Load model
    print("[3/7] Loading 'all-MiniLM-L6-v2' model...")
    start_load = time.time()
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        load_time = time.time() - start_load
        print(f"✓ Model loaded successfully in {load_time:.2f} seconds")
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False
    print()
    
    # Test 4: Memory after loading
    print("[4/7] Measuring memory footprint after loading...")
    memory_after, peak_memory = get_current_memory_mb()
    memory_used = memory_after - memory_before
    print(f"✓ Memory after load: {memory_after:.2f} MB")
    print(f"✓ Peak memory usage: {peak_memory:.2f} MB")
    print(f"✓ Model footprint (estimated): {memory_used:.2f} MB")
    if peak_memory > 500:
        print(f"⚠ Warning: Peak memory ({peak_memory:.2f} MB) exceeds soft limit (500 MB)")
    print()
    
    # Test 5: Generate sample embeddings
    print("[5/7] Generating 10 sample embeddings (5 reviews + 5 book descriptions)...")
    try:
        sample_texts = [
            # Review texts
            "This book is absolutely amazing and I loved every page of it!",
            "The protagonist's character development was outstanding throughout the story.",
            "I found this book to be predictable and somewhat disappointing.",
            "The writing style was beautiful and kept me engaged until the end.",
            "A thought-provoking narrative that challenges conventional thinking.",
            # Book description texts
            "A thrilling adventure story set in a dystopian future.",
            "This novel explores themes of love, loss, and redemption.",
            "An epic fantasy saga with complex characters and intricate world-building.",
            "A mystery thriller with unexpected twists at every turn.",
            "A profound meditation on human nature and morality."
        ]
        
        embeddings = model.encode(sample_texts)
        embedding_shape = embeddings.shape
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"✓ Embedding shape: {embedding_shape}")
        print(f"✓ Expected dimension: 384, Actual: {embedding_shape[1]}")
        
        if embedding_shape[1] != 384:
            print(f"✗ Embedding dimension mismatch! Expected 384, got {embedding_shape[1]}")
            return False
        else:
            print(f"✓ Embedding dimension correct!")
    except Exception as e:
        print(f"✗ Embedding generation failed: {e}")
        return False
    print()
    
    # Test 6: Latency test (100 predictions with batch processing)
    print("[6/7] Performance test: 100 predictions (batch processing)...")
    latency_texts = [
        "This is a test review for the book.",
        "The book exceeded my expectations.",
    ]
    
    try:
        start_latency = time.time()
        # Batch process: more efficient than individual calls
        for _ in range(5):  # 5 batches × 20 texts = 100 predictions
            _ = model.encode(latency_texts * 10, convert_to_numpy=True)
        total_latency = time.time() - start_latency
        avg_latency_per_prediction = (total_latency / 100) * 1000  # Convert to ms
        
        print(f"✓ 100 predictions completed in {total_latency:.3f} seconds")
        print(f"✓ Average latency: {avg_latency_per_prediction:.2f} ms per prediction")
        
        # Note: CPU latency thresholds are more generous than GPU
        # GPU: ~5ms per prediction, CPU: ~10-15ms per prediction
        if total_latency > 2.0:
            print(f"⚠ Warning: Total latency ({total_latency:.3f}s) is slower than expected")
        else:
            print(f"✓ Latency acceptable for CPU inference")
    except Exception as e:
        print(f"✗ Latency test failed: {e}")
        return False
    print()
    
    # Test 7: Summary and validation
    print("[7/7] VALIDATION SUMMARY")
    print("-" * 70)
    validation_results = {
        "Model import successful": True,
        "Model loads successfully": load_time > 0,
        "Memory footprint reasonable (< 300MB total)": memory_used < 300,
        "Embedding dimension correct (384)": embedding_shape[1] == 384,
        "Inference latency acceptable (CPU)": total_latency < 2.0,
    }
    
    all_passed = True
    for check, passed in validation_results.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")
        if not passed:
            all_passed = False
    
    print("-" * 70)
    print()
    
    # Final result
    if all_passed:
        print("=" * 70)
        print("SUCCESS! All tests passed. ✓")
        print("=" * 70)
        print()
        print("SUMMARY STATISTICS:")
        print(f"  Model Load Time (cached):  {load_time:.2f} seconds")
        print(f"  Memory Baseline:           {memory_before:.2f} MB")
        print(f"  Memory After Load:         {memory_after:.2f} MB")
        print(f"  Memory Increase:           {memory_used:.2f} MB")
        print(f"  Peak Memory:               {peak_memory:.2f} MB")
        print(f"  Embedding Dimension:       {embedding_shape[1]}")
        print(f"  100 Predictions Latency:   {total_latency:.3f} seconds ({avg_latency_per_prediction:.2f} ms/pred)")
        print()
        print("NOTE: Running on CPU. GPU deployment would see ~2-3x faster latency.")
        print("Ready for Phase 2 implementation! 🚀")
        print("=" * 70)
        return True
    else:
        print("=" * 70)
        print("FAILURE: Some tests did not pass. ✗")
        print("=" * 70)
        return False


if __name__ == "__main__":
    try:
        success = test_sentence_transformer()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
