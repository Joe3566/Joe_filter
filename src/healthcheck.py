#!/usr/bin/env python3
"""
Docker Health Check Script for Enterprise Compliance Filter
Performs comprehensive health checks for container orchestration
"""

import sys
import os
import requests
import time
import json
from urllib.parse import urljoin

def health_check():
    """Perform comprehensive health check"""
    try:
        base_url = f"http://localhost:{os.environ.get('PORT', 5000)}"
        timeout = 10
        
        # Check if the application is responding
        health_url = urljoin(base_url, '/health')
        
        start_time = time.time()
        response = requests.get(health_url, timeout=timeout)
        response_time = (time.time() - start_time) * 1000
        
        # Check response status
        if response.status_code != 200:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
        
        # Parse health check response
        try:
            health_data = response.json()
            
            if health_data.get('status') != 'healthy':
                print(f"❌ Application reports unhealthy status: {health_data}")
                return False
            
            # Check individual components
            components = health_data.get('components', {})
            for component, status in components.items():
                if status != 'healthy':
                    print(f"❌ Component {component} is {status}")
                    return False
            
            print(f"✅ Health check passed ({response_time:.2f}ms)")
            print(f"📊 Components: {list(components.keys())}")
            
            # Additional checks
            if response_time > 5000:  # 5 seconds
                print(f"⚠️  Slow response time: {response_time:.2f}ms")
            
            return True
            
        except json.JSONDecodeError:
            print("❌ Invalid JSON response from health endpoint")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to application")
        return False
    
    except requests.exceptions.Timeout:
        print(f"❌ Health check timed out after {timeout}s")
        return False
    
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False

def readiness_check():
    """Check if application is ready to serve traffic"""
    try:
        base_url = f"http://localhost:{os.environ.get('PORT', 5000)}"
        ready_url = urljoin(base_url, '/ready')
        
        response = requests.get(ready_url, timeout=5)
        
        if response.status_code == 200:
            ready_data = response.json()
            if ready_data.get('status') == 'ready':
                print("✅ Application is ready")
                return True
        
        print("❌ Application is not ready")
        return False
        
    except Exception as e:
        print(f"❌ Readiness check failed: {e}")
        return False

def main():
    """Main health check function"""
    print("🔍 Starting Docker health check...")
    
    # Perform readiness check first
    if not readiness_check():
        sys.exit(1)
    
    # Perform detailed health check
    if not health_check():
        sys.exit(1)
    
    print("🎉 All health checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()