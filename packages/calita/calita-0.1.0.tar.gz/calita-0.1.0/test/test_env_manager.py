#!/usr/bin/env python3
"""
Test script to verify the modified EnvironmentManager functionality.
"""
import os
import sys
import yaml

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calita.env_manager import EnvironmentManager

def test_dependency_installation():
    """Test the modified dependency installation with python -m pip."""
    
    print("Testing EnvironmentManager dependency installation...")
    
    try:
        # Load configuration
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize EnvironmentManager
        em = EnvironmentManager(config)
        print(f"EnvironmentManager initialized with prefix: {em.env_prefix}")
        
        # Test dependency installation on existing environment
        test_env = "test_env_creation"
        test_dependencies = ["requests>=2.25.0"]
        
        print(f"Testing dependency installation in environment: {em._get_full_env_name(test_env)}")
        print(f"Dependencies to install: {test_dependencies}")
        
        # Install dependencies
        result = em.install_dependencies(test_env, test_dependencies)
        
        print(f"Installation result: {result}")
        
        if result:
            print("✅ Dependency installation test PASSED")
        else:
            print("❌ Dependency installation test FAILED")
            
        return result
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dependency_installation()
    sys.exit(0 if success else 1)