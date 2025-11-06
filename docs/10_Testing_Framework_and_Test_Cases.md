# Testing Framework and Test Cases - LLM Compliance Filter System

## Document Information
- **Document Title**: Testing Framework and Test Cases
- **Project**: LLM Compliance Filter System
- **Version**: 1.0
- **Date**: 2024-09-16
- **Related Documents**: System Requirements Specification (SRS)

---

## 1. Testing Strategy Overview

### 1.1 Testing Objectives
- Validate all functional requirements are implemented correctly
- Verify non-functional requirements are met (performance, security, usability)
- Ensure system reliability and stability under various conditions
- Validate compliance with regulatory requirements
- Confirm system scalability and maintainability

### 1.2 Testing Types

#### Unit Testing
- **Coverage Target**: 90%+ code coverage
- **Framework**: pytest for Python components
- **Scope**: Individual functions, classes, and modules
- **Responsibility**: Development team

#### Integration Testing
- **Scope**: API endpoints, database interactions, external services
- **Tools**: pytest with requests library, database fixtures
- **Responsibility**: Development and QA teams

#### Performance Testing
- **Tools**: Apache JMeter, Locust, or k6
- **Scope**: Load testing, stress testing, spike testing
- **Responsibility**: DevOps and QA teams

#### Security Testing
- **Tools**: OWASP ZAP, Burp Suite, security scanners
- **Scope**: Vulnerability assessment, penetration testing
- **Responsibility**: Security team

#### User Acceptance Testing
- **Scope**: End-to-end workflows, user scenarios
- **Responsibility**: Business users, QA team

---

## 2. Functional Test Cases

### 2.1 Core Processing Test Cases

#### TC-001: Single Text Compliance Check
**Requirement**: FR-001  
**Priority**: Critical

```python
def test_single_text_compliance_check():
    """Test single text compliance analysis"""
    
    # Test data
    test_cases = [
        {
            "input": "Hello world, how are you?",
            "expected_action": "ALLOW",
            "expected_score_range": (0.0, 0.3)
        },
        {
            "input": "Contact me at john.doe@company.com",
            "expected_action": "BLOCK",
            "expected_score_range": (0.7, 1.0),
            "expected_violations": ["email"]
        },
        {
            "input": "Call me at (555) 123-4567",
            "expected_action": "WARN",
            "expected_score_range": (0.5, 0.7),
            "expected_violations": ["phone"]
        }
    ]
    
    for case in test_cases:
        response = client.post("/api/check", json={"text": case["input"]})
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["action"] == case["expected_action"]
        assert case["expected_score_range"][0] <= result["score"] <= case["expected_score_range"][1]
        assert result["processing_time"] < 0.2  # 200ms requirement
        
        if "expected_violations" in case:
            violation_types = [v["type"] for v in result["violations"]]
            for expected_violation in case["expected_violations"]:
                assert expected_violation in violation_types
```

#### TC-002: Privacy Violation Detection
**Requirement**: FR-002  
**Priority**: Critical

```python
def test_privacy_violation_detection():
    """Test privacy violation detection accuracy"""
    
    privacy_test_cases = [
        # Email detection
        {
            "text": "Please contact support@company.com for assistance",
            "violation_type": "email",
            "expected_confidence": 0.95,
            "expected_detected": True
        },
        # Phone number detection
        {
            "text": "Our phone number is +1 (555) 123-4567",
            "violation_type": "phone", 
            "expected_confidence": 0.90,
            "expected_detected": True
        },
        # SSN detection
        {
            "text": "My SSN is 123-45-6789",
            "violation_type": "ssn",
            "expected_confidence": 0.98,
            "expected_detected": True
        },
        # Credit card detection
        {
            "text": "My card number is 4532-1234-5678-9012",
            "violation_type": "credit_card",
            "expected_confidence": 0.95,
            "expected_detected": True
        },
        # False positive test
        {
            "text": "The temperature is 98.6 degrees",
            "violation_type": "phone",
            "expected_detected": False
        }
    ]
    
    for case in privacy_test_cases:
        response = client.post("/api/check", json={"text": case["text"]})
        result = response.json()
        
        violations = [v for v in result["violations"] if v["type"] == case["violation_type"]]
        
        if case["expected_detected"]:
            assert len(violations) > 0, f"Failed to detect {case['violation_type']}"
            violation = violations[0]
            assert violation["confidence"] >= case["expected_confidence"]
        else:
            assert len(violations) == 0, f"False positive for {case['violation_type']}"
```

#### TC-003: Batch Processing
**Requirement**: FR-004  
**Priority**: High

```python
def test_batch_processing():
    """Test batch processing functionality"""
    
    batch_texts = [
        "Hello world",
        "Contact john@example.com for more info",
        "Call us at (555) 123-4567",
        "This is inappropriate toxic content",
        "Normal text without violations"
    ]
    
    # Test basic batch processing
    response = client.post("/api/batch", json={"texts": batch_texts})
    
    assert response.status_code == 200
    result = response.json()
    
    assert "results" in result
    assert len(result["results"]) == len(batch_texts)
    assert "total_time" in result
    assert "throughput" in result
    
    # Verify results order is maintained
    for i, batch_result in enumerate(result["results"]):
        assert "action" in batch_result
        assert "score" in batch_result
        assert batch_result["text_index"] == i
    
    # Test large batch (performance requirement)
    large_batch = ["Test text"] * 1000
    start_time = time.time()
    response = client.post("/api/batch", json={"texts": large_batch})
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    assert processing_time < 10.0  # Should process 1000 texts in under 10 seconds
```

### 2.2 API Integration Test Cases

#### TC-004: API Authentication
**Requirement**: FR-008  
**Priority**: High

```python
def test_api_authentication():
    """Test API authentication mechanisms"""
    
    # Test without authentication
    response = client.post("/api/check", json={"text": "test"})
    assert response.status_code == 401
    
    # Test with invalid API key
    headers = {"Authorization": "Bearer invalid_key"}
    response = client.post("/api/check", json={"text": "test"}, headers=headers)
    assert response.status_code == 401
    
    # Test with valid API key
    headers = {"Authorization": f"Bearer {valid_api_key}"}
    response = client.post("/api/check", json={"text": "test"}, headers=headers)
    assert response.status_code == 200
    
    # Test rate limiting
    for i in range(101):  # Exceed rate limit of 100 requests/minute
        response = client.post("/api/check", json={"text": f"test {i}"}, headers=headers)
    
    assert response.status_code == 429  # Rate limit exceeded
```

#### TC-005: Configuration Management
**Requirement**: FR-006  
**Priority**: High

```python
def test_configuration_management():
    """Test dynamic configuration updates"""
    
    # Get current configuration
    response = client.get("/api/config", headers=auth_headers)
    assert response.status_code == 200
    original_config = response.json()
    
    # Update thresholds
    new_config = original_config.copy()
    new_config["thresholds"]["block_threshold"] = 0.8
    
    response = client.put("/api/config", json=new_config, headers=auth_headers)
    assert response.status_code == 200
    
    # Verify configuration was updated
    response = client.get("/api/config", headers=auth_headers)
    updated_config = response.json()
    assert updated_config["thresholds"]["block_threshold"] == 0.8
    
    # Test configuration validation
    invalid_config = original_config.copy()
    invalid_config["thresholds"]["block_threshold"] = 1.5  # Invalid value
    
    response = client.put("/api/config", json=invalid_config, headers=auth_headers)
    assert response.status_code == 400
    
    # Restore original configuration
    client.put("/api/config", json=original_config, headers=auth_headers)
```

---

## 3. Non-Functional Test Cases

### 3.1 Performance Test Cases

#### TC-006: Response Time Requirements
**Requirement**: NFR-001  
**Priority**: Critical

```python
def test_response_time_requirements():
    """Test response time requirements"""
    
    response_times = []
    
    # Test 100 single requests
    for i in range(100):
        start_time = time.time()
        response = client.post("/api/check", json={"text": f"Test message {i}"})
        end_time = time.time()
        
        assert response.status_code == 200
        response_times.append(end_time - start_time)
    
    # Calculate percentiles
    response_times.sort()
    p95_time = response_times[int(0.95 * len(response_times))]
    p99_time = response_times[int(0.99 * len(response_times))]
    
    # Verify requirements
    assert p95_time < 0.2, f"95th percentile response time {p95_time} exceeds 200ms"
    assert p99_time < 0.5, f"99th percentile response time {p99_time} exceeds 500ms"
```

#### TC-007: Load Testing
**Requirement**: NFR-002  
**Priority**: Critical

```python
def test_concurrent_load():
    """Test system under concurrent load"""
    
    import concurrent.futures
    import threading
    
    def make_request():
        response = client.post("/api/check", json={"text": "Load test message"})
        return response.status_code == 200
    
    # Test with 1000 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(1000)]
        
        successful_requests = sum(1 for future in concurrent.futures.as_completed(futures) if future.result())
    
    # Should handle at least 95% of requests successfully
    success_rate = successful_requests / 1000
    assert success_rate >= 0.95, f"Success rate {success_rate} below 95%"
```

#### TC-008: Caching Performance
**Requirement**: NFR-001.3  
**Priority**: High

```python
def test_caching_performance():
    """Test caching performance requirements"""
    
    test_text = "This is a test message for cache performance"
    
    # First request (cache miss)
    start_time = time.time()
    response = client.post("/api/check", json={"text": test_text})
    cache_miss_time = time.time() - start_time
    
    assert response.status_code == 200
    
    # Second request (cache hit)
    start_time = time.time()
    response = client.post("/api/check", json={"text": test_text})
    cache_hit_time = time.time() - start_time
    
    assert response.status_code == 200
    
    # Cache hit should be significantly faster
    assert cache_hit_time < 0.05, f"Cache hit time {cache_hit_time} exceeds 50ms"
    assert cache_hit_time < cache_miss_time * 0.1, "Cache hit not significantly faster than miss"
```

### 3.2 Security Test Cases

#### TC-009: Data Encryption
**Requirement**: NFR-007  
**Priority**: Critical

```python
def test_data_encryption():
    """Test data encryption requirements"""
    
    # Test HTTPS enforcement
    http_response = requests.post("http://localhost:8080/api/check", 
                                 json={"text": "test"})
    
    # Should redirect to HTTPS or return 403
    assert http_response.status_code in [301, 302, 403]
    
    # Test TLS version
    import ssl
    import socket
    
    context = ssl.create_default_context()
    with socket.create_connection(('localhost', 443)) as sock:
        with context.wrap_socket(sock, server_hostname='localhost') as ssock:
            assert ssock.version() in ['TLSv1.3', 'TLSv1.2']
```

#### TC-010: Input Validation
**Requirement**: NFR-006  
**Priority**: High

```python
def test_input_validation():
    """Test input validation and sanitization"""
    
    # Test oversized input
    large_text = "A" * 20000  # Exceeds 10,000 character limit
    response = client.post("/api/check", json={"text": large_text})
    assert response.status_code == 400
    
    # Test SQL injection attempt
    sql_injection = "'; DROP TABLE users; --"
    response = client.post("/api/check", json={"text": sql_injection})
    assert response.status_code == 200  # Should process safely
    
    # Test XSS attempt
    xss_attempt = "<script>alert('xss')</script>"
    response = client.post("/api/check", json={"text": xss_attempt})
    assert response.status_code == 200  # Should process safely
    
    # Test invalid JSON
    response = client.post("/api/check", data="invalid json")
    assert response.status_code == 400
```

### 3.3 Reliability Test Cases

#### TC-011: Error Handling
**Requirement**: NFR-006  
**Priority**: High

```python
def test_error_handling():
    """Test system error handling"""
    
    # Test database connection failure simulation
    with mock.patch('database.get_connection', side_effect=ConnectionError):
        response = client.post("/api/check", json={"text": "test"})
        
        # Should return graceful error, not crash
        assert response.status_code == 503
        assert "service unavailable" in response.json()["message"].lower()
    
    # Test model loading failure
    with mock.patch('transformers.pipeline', side_effect=Exception("Model load failed")):
        response = client.post("/api/check", json={"text": "test"})
        
        # Should degrade gracefully to privacy-only detection
        assert response.status_code == 200
        result = response.json()
        assert "error" not in result
```

#### TC-012: Failover Testing
**Requirement**: NFR-005  
**Priority**: High

```python
def test_failover_mechanisms():
    """Test automatic failover capabilities"""
    
    # This would require a multi-instance setup
    # Simplified test for demonstration
    
    # Test Redis failover (if Redis unavailable, should continue with L1 cache)
    with mock.patch('redis.Redis', side_effect=ConnectionError):
        response = client.post("/api/check", json={"text": "failover test"})
        assert response.status_code == 200
    
    # Test model failover (if primary model fails, use fallback)
    with mock.patch('transformers.pipeline') as mock_pipeline:
        mock_pipeline.side_effect = [Exception("Model failed"), mock.MagicMock()]
        
        response = client.post("/api/check", json={"text": "model failover test"})
        assert response.status_code == 200
        assert mock_pipeline.call_count == 2  # Tried fallback
```

---

## 4. Load Testing Scenarios

### 4.1 Sustained Load Test
**Objective**: Verify system handles expected production load

```yaml
# JMeter Test Plan
test_plan:
  name: "Sustained Load Test"
  duration: "10 minutes"
  ramp_up: "2 minutes"
  
  thread_groups:
    - name: "API Load Test"
      threads: 100
      ramp_up_period: 120
      duration: 600
      
      requests:
        - name: "Single Check"
          method: POST
          path: "/api/check"
          weight: 80%
          body: '{"text": "Test message ${__counter()}"}'
          
        - name: "Batch Check"
          method: POST
          path: "/api/batch"
          weight: 20%
          body: '{"texts": ["Text 1", "Text 2", "Text 3"]}'

  assertions:
    - response_time_p95 < 200ms
    - error_rate < 0.1%
    - throughput > 100 requests/second
```

### 4.2 Spike Testing
**Objective**: Verify system handles traffic spikes

```yaml
spike_test:
  name: "Traffic Spike Test"
  phases:
    - name: "Normal Load"
      duration: "2 minutes"
      users: 50
      
    - name: "Spike"
      duration: "30 seconds" 
      users: 500
      
    - name: "Recovery"
      duration: "5 minutes"
      users: 50

  success_criteria:
    - no_system_crashes
    - recovery_time < 60_seconds
    - error_rate_spike < 5%
```

---

## 5. Automated Testing Pipeline

### 5.1 Continuous Integration Tests

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run unit tests
        run: pytest tests/unit/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Run integration tests
        run: pytest tests/integration/
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test
          REDIS_URL: redis://localhost:6379

  performance-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - name: Setup test environment
        run: docker-compose -f docker-compose.test.yml up -d
      - name: Run performance tests
        run: |
          pip install locust
          locust -f tests/performance/locustfile.py --headless \
                 -u 100 -r 10 -t 300s --host=http://localhost:8080
```

### 5.2 Test Reporting

```python
# tests/conftest.py
import pytest
import json
from datetime import datetime

@pytest.fixture(scope="session", autouse=True)
def test_report(request):
    """Generate test execution report"""
    
    def generate_report():
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "environment": "test",
                "total_tests": request.session.testscollected,
                "passed": request.session.testspassed,
                "failed": request.session.testsfailed,
                "skipped": request.session.testsskipped
            },
            "performance_metrics": {
                # Collected during test execution
            },
            "coverage_report": {
                # Generated by pytest-cov
            }
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
    
    request.addfinalizer(generate_report)
```

---

## 6. Test Environment Setup

### 6.1 Test Data Management

```python
# tests/fixtures/test_data.py
import pytest
from faker import Faker

fake = Faker()

@pytest.fixture
def privacy_test_data():
    """Generate test data for privacy detection"""
    return {
        "emails": [fake.email() for _ in range(100)],
        "phones": [fake.phone_number() for _ in range(100)],
        "ssns": [fake.ssn() for _ in range(50)],
        "credit_cards": [fake.credit_card_number() for _ in range(50)],
        "addresses": [fake.address() for _ in range(100)]
    }

@pytest.fixture
def compliance_test_scenarios():
    """Predefined test scenarios for compliance checking"""
    return [
        {
            "category": "clean_content",
            "texts": [
                "How does machine learning work?",
                "What's the weather like today?",
                "Can you help with my homework?"
            ],
            "expected_action": "ALLOW"
        },
        {
            "category": "privacy_violations", 
            "texts": [
                "My email is user@example.com",
                "Call me at (555) 123-4567",
                "SSN: 123-45-6789"
            ],
            "expected_action": "BLOCK"
        },
        {
            "category": "borderline_content",
            "texts": [
                "Visit our website at company dot com",
                "Contact us for more information",
                "Our support team can help"
            ],
            "expected_action": "WARN"
        }
    ]
```

### 6.2 Mock Services

```python
# tests/mocks/mock_services.py
from unittest.mock import Mock, MagicMock
import pytest

@pytest.fixture
def mock_transformers_pipeline():
    """Mock transformers pipeline for testing"""
    mock_pipeline = Mock()
    mock_pipeline.return_value = [
        {"label": "TOXIC", "score": 0.1},
        {"label": "NON_TOXIC", "score": 0.9}
    ]
    return mock_pipeline

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.ping.return_value = True
    return mock_redis
```

---

This comprehensive testing framework ensures that all functional and non-functional requirements are thoroughly validated through automated tests that can be integrated into your CI/CD pipeline. The tests cover everything from unit-level functionality to system-wide performance and security requirements.
