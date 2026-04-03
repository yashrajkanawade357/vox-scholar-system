import os
import sys

def test_vox_structure():
    """Test 1: Verify vox_service folder and core files exist."""
    required_files = [
        "vox_service/main.py",
        "vox_service/vox_logic.py",
        "vox_service/rag_pipeline.py"
    ]
    for f in required_files:
        if not os.path.exists(f):
            print(f"FAIL: Missing {f}")
            return False
    print("PASS: VOX Service structure is correct.")
    return True

def test_scholar_structure():
    """Test 2: Verify scholar_ui folder and core files exist."""
    required_files = [
        "scholar_ui/app.py",
        "scholar_ui/scanner.py",
        "scholar_ui/llm_engine.py"
    ]
    for f in required_files:
        if not os.path.exists(f):
            print(f"FAIL: Missing {f}")
            return False
    print("PASS: Scholar UI structure is correct.")
    return True

def test_config_load():
    """Test 3: Verify core/config.py can be imported and env vars are set."""
    try:
        from core.config import VOX_SERVICE_URL, SCHOLAR_SERVICE_URL
        if not VOX_SERVICE_URL or not SCHOLAR_SERVICE_URL:
            print("FAIL: Config variables are empty.")
            return False
        print("PASS: Core configuration loaded successfully.")
        return True
    except Exception as e:
        print(f"FAIL: Could not load config - {e}")
        return False

if __name__ == "__main__":
    print("--- Running Unified System Integration Tests ---")
    results = [
        test_vox_structure(),
        test_scholar_structure(),
        test_config_load()
    ]
    
    if all(results):
        print("\nSUMMARY: ALL 3 TESTS PASSED")
        sys.exit(0)
    else:
        print("\nSUMMARY: INTEGRATION TESTS FAILED")
        sys.exit(1)
