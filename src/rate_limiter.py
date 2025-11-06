#!/usr/bin/env python3
"""
🛡️ Rate Limiting & Abuse Prevention
Protects the compliance filter from abuse and excessive usage
"""

import time
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10  # Allow short bursts
    cooldown_seconds: int = 300  # 5 minute cooldown after violation
    

@dataclass
class ClientStats:
    """Statistics for a client"""
    minute_requests: deque = field(default_factory=deque)
    hour_requests: deque = field(default_factory=deque)
    day_requests: deque = field(default_factory=deque)
    violations: int = 0
    cooldown_until: Optional[float] = None
    first_seen: float = field(default_factory=time.time)
    total_requests: int = 0
    flagged_content_count: int = 0
    suspicious_patterns: int = 0


class RateLimiter:
    """Advanced rate limiting with abuse detection"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.clients: Dict[str, ClientStats] = defaultdict(ClientStats)
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        
    def check_rate_limit(self, client_id: str) -> Tuple[bool, str]:
        """
        Check if client is within rate limits
        Returns: (allowed: bool, reason: str)
        """
        current_time = time.time()
        stats = self.clients[client_id]
        
        # Check if client is in cooldown
        if stats.cooldown_until and current_time < stats.cooldown_until:
            remaining = int(stats.cooldown_until - current_time)
            return False, f"Rate limit exceeded. Try again in {remaining} seconds"
        
        # Check if IP is blocked
        if client_id in self.blocked_ips:
            if current_time < self.blocked_ips[client_id]:
                remaining = int(self.blocked_ips[client_id] - current_time)
                return False, f"IP blocked for abuse. Unblocked in {remaining} seconds"
            else:
                # Unblock
                del self.blocked_ips[client_id]
        
        # Clean old requests
        self._clean_old_requests(stats, current_time)
        
        # Check minute limit
        if len(stats.minute_requests) >= self.config.requests_per_minute:
            self._apply_cooldown(stats, current_time)
            return False, f"Too many requests. Limit: {self.config.requests_per_minute}/minute"
        
        # Check hour limit
        if len(stats.hour_requests) >= self.config.requests_per_hour:
            self._apply_cooldown(stats, current_time)
            return False, f"Hourly limit exceeded. Limit: {self.config.requests_per_hour}/hour"
        
        # Check day limit
        if len(stats.day_requests) >= self.config.requests_per_day:
            self._apply_cooldown(stats, current_time)
            return False, f"Daily limit exceeded. Limit: {self.config.requests_per_day}/day"
        
        # Check for burst attacks
        if self._detect_burst_attack(stats, current_time):
            self._apply_cooldown(stats, current_time)
            return False, "Burst attack detected. Rate limit applied"
        
        # All checks passed
        return True, "OK"
    
    def record_request(self, client_id: str, flagged: bool = False, suspicious: bool = False):
        """Record a request from a client"""
        current_time = time.time()
        stats = self.clients[client_id]
        
        stats.minute_requests.append(current_time)
        stats.hour_requests.append(current_time)
        stats.day_requests.append(current_time)
        stats.total_requests += 1
        
        if flagged:
            stats.flagged_content_count += 1
        
        if suspicious:
            stats.suspicious_patterns += 1
            
        # Auto-block if too many violations
        if stats.flagged_content_count > 50:  # >50 flagged in a day
            self._block_ip(client_id, duration=86400)  # 24 hours
        elif stats.suspicious_patterns > 20:  # >20 suspicious patterns
            self._block_ip(client_id, duration=3600)  # 1 hour
    
    def _clean_old_requests(self, stats: ClientStats, current_time: float):
        """Remove requests outside the time windows"""
        # Minute window
        while stats.minute_requests and current_time - stats.minute_requests[0] > 60:
            stats.minute_requests.popleft()
        
        # Hour window
        while stats.hour_requests and current_time - stats.hour_requests[0] > 3600:
            stats.hour_requests.popleft()
        
        # Day window
        while stats.day_requests and current_time - stats.day_requests[0] > 86400:
            stats.day_requests.popleft()
    
    def _detect_burst_attack(self, stats: ClientStats, current_time: float) -> bool:
        """Detect sudden burst of requests (potential attack)"""
        if len(stats.minute_requests) < self.config.burst_size:
            return False
        
        # Check if last N requests came within 5 seconds
        recent_requests = list(stats.minute_requests)[-self.config.burst_size:]
        time_span = current_time - recent_requests[0]
        
        return time_span < 5.0  # All within 5 seconds = burst
    
    def _apply_cooldown(self, stats: ClientStats, current_time: float):
        """Apply cooldown period to a client"""
        stats.cooldown_until = current_time + self.config.cooldown_seconds
        stats.violations += 1
    
    def _block_ip(self, client_id: str, duration: int = 3600):
        """Block an IP address"""
        self.blocked_ips[client_id] = time.time() + duration
    
    def get_client_stats(self, client_id: str) -> Dict:
        """Get statistics for a client"""
        stats = self.clients[client_id]
        current_time = time.time()
        
        return {
            'total_requests': stats.total_requests,
            'flagged_content': stats.flagged_content_count,
            'suspicious_patterns': stats.suspicious_patterns,
            'violations': stats.violations,
            'in_cooldown': stats.cooldown_until and current_time < stats.cooldown_until,
            'is_blocked': client_id in self.blocked_ips,
            'minute_usage': f"{len(stats.minute_requests)}/{self.config.requests_per_minute}",
            'hour_usage': f"{len(stats.hour_requests)}/{self.config.requests_per_hour}",
            'day_usage': f"{len(stats.day_requests)}/{self.config.requests_per_day}",
        }
    
    def unblock_ip(self, client_id: str):
        """Manually unblock an IP"""
        if client_id in self.blocked_ips:
            del self.blocked_ips[client_id]
        if client_id in self.clients:
            self.clients[client_id].cooldown_until = None
    
    def get_blocked_ips(self) -> Dict[str, int]:
        """Get list of blocked IPs with remaining time"""
        current_time = time.time()
        return {
            ip: int(unblock_time - current_time)
            for ip, unblock_time in self.blocked_ips.items()
            if unblock_time > current_time
        }


def get_client_id(request) -> str:
    """Extract client identifier from Flask request"""
    # Try to get real IP (considering proxies)
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    
    # Hash IP for privacy
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


# Demo
if __name__ == "__main__":
    print("🛡️ Rate Limiter Demo\\n")
    print("=" * 80)
    
    limiter = RateLimiter(RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        requests_per_day=100
    ))
    
    client = "test_client_123"
    
    print(f"\\nTesting normal usage:")
    for i in range(3):
        allowed, reason = limiter.check_rate_limit(client)
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - {reason}")
        if allowed:
            limiter.record_request(client)
    
    print(f"\\nTesting burst attack (6 rapid requests):")
    for i in range(6):
        allowed, reason = limiter.check_rate_limit(client)
        print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'} - {reason}")
        if allowed:
            limiter.record_request(client)
        time.sleep(0.1)
    
    print(f"\\nClient stats:")
    stats = limiter.get_client_stats(client)
    for key, value in stats.items():
        print(f"  {key}: {value}")
