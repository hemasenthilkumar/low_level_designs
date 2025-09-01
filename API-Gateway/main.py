# Create a simple test file in your root directory
# test_structure.py

try:
    import config
    import data_structures
    import components
    import tests
    print("✅ All packages imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")