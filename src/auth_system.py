#!/usr/bin/env python3
"""
Modern Authentication System for Enhanced Compliance Filter
Supports JWT, OAuth 2.0, MFA, API Keys, and RBAC
"""

import jwt
import hashlib
import secrets
import pyotp
import qrcode
import io
import base64
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
import sqlite3
from functools import wraps
from flask import request, jsonify, session
import requests

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    MODERATOR = "moderator" 
    ANALYST = "analyst"
    VIEWER = "viewer"

class AuthProvider(Enum):
    """Authentication providers"""
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"

@dataclass
class User:
    """User model"""
    id: int
    username: str
    email: str
    role: UserRole
    provider: AuthProvider
    is_active: bool
    is_verified: bool
    has_mfa: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    mfa_secret: Optional[str] = None
    api_key_hash: Optional[str] = None

@dataclass
class AuthToken:
    """JWT token model"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600

class AuthenticationError(Exception):
    """Authentication related errors"""
    pass

class AuthSystem:
    """Modern authentication system with multiple methods"""
    
    def __init__(self, secret_key: str = None, db_path: str = "auth.db"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.db_path = db_path
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
        
        # OAuth configurations
        self.oauth_configs = {
            "google": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile"
            },
            "github": {
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "auth_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scope": "user:email"
            },
            "microsoft": {
                "client_id": os.getenv("MICROSOFT_CLIENT_ID"),
                "client_secret": os.getenv("MICROSOFT_CLIENT_SECRET"),
                "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "scope": "openid email profile"
            }
        }
        
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                role TEXT NOT NULL DEFAULT 'viewer',
                provider TEXT NOT NULL DEFAULT 'local',
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                has_mfa BOOLEAN DEFAULT 0,
                mfa_secret TEXT,
                api_key_hash TEXT,
                oauth_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        """)
        
        # Create sessions table for refresh tokens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT 0,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Create default admin user if none exists
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        try:
            existing_admin = self.get_user_by_username("admin")
            if not existing_admin:
                self.create_user(
                    username="admin",
                    email="admin@compliance-filter.local",
                    password="CompliantFilter2025!",
                    role=UserRole.ADMIN
                )
                logger.info("✅ Default admin user created (username: admin)")
        except Exception as e:
            logger.warning(f"Could not create default admin: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{pwd_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return pwd_hash.hex() == stored_hash
        except:
            return False
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return f"cf_{secrets.token_urlsafe(32)}"
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str = None, 
                   role: UserRole = UserRole.VIEWER, provider: AuthProvider = AuthProvider.LOCAL,
                   oauth_id: str = None) -> User:
        """Create new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password) if password else None
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, provider, oauth_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, role.value, provider.value, oauth_id))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                role=role,
                provider=provider,
                is_active=True,
                is_verified=provider != AuthProvider.LOCAL,  # OAuth users are auto-verified
                has_mfa=False,
                created_at=datetime.now(timezone.utc)
            )
            
            self._audit_log(user_id, "user_created", True, f"User {username} created")
            return user
            
        except sqlite3.IntegrityError as e:
            raise AuthenticationError(f"User already exists: {e}")
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> Optional[User]:
        """Authenticate user with username/password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if account is locked
            cursor.execute("""
                SELECT id, username, email, password_hash, role, provider, is_active, 
                       is_verified, has_mfa, mfa_secret, login_attempts, locked_until
                FROM users 
                WHERE username = ? OR email = ?
            """, (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                self._audit_log(None, "login_attempt", False, f"User {username} not found", ip_address, user_agent)
                return None
            
            user_id, user_username, email, password_hash, role, provider, is_active, is_verified, has_mfa, mfa_secret, login_attempts, locked_until = user_data
            
            # Check if account is locked
            if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                self._audit_log(user_id, "login_attempt", False, "Account locked", ip_address, user_agent)
                raise AuthenticationError("Account is temporarily locked")
            
            # Check if account is active
            if not is_active:
                self._audit_log(user_id, "login_attempt", False, "Account inactive", ip_address, user_agent)
                raise AuthenticationError("Account is inactive")
            
            # Verify password
            if not password_hash or not self.verify_password(password, password_hash):
                # Increment login attempts
                new_attempts = login_attempts + 1
                lock_time = None
                
                if new_attempts >= 5:  # Lock after 5 failed attempts
                    lock_time = (datetime.now() + timedelta(minutes=30)).isoformat()
                
                cursor.execute("""
                    UPDATE users 
                    SET login_attempts = ?, locked_until = ?
                    WHERE id = ?
                """, (new_attempts, lock_time, user_id))
                conn.commit()
                
                self._audit_log(user_id, "login_attempt", False, f"Invalid password (attempt {new_attempts})", ip_address, user_agent)
                return None
            
            # Reset login attempts on successful authentication
            cursor.execute("""
                UPDATE users 
                SET login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            
            user = User(
                id=user_id,
                username=user_username,
                email=email,
                role=UserRole(role),
                provider=AuthProvider(provider),
                is_active=is_active,
                is_verified=is_verified,
                has_mfa=has_mfa,
                mfa_secret=mfa_secret,
                created_at=datetime.now(timezone.utc),
                last_login=datetime.now(timezone.utc)
            )
            
            self._audit_log(user_id, "login_success", True, "Password authentication", ip_address, user_agent)
            return user
            
        finally:
            conn.close()
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate using API key"""
        if not api_key.startswith("cf_"):
            return None
        
        api_key_hash = self.hash_api_key(api_key)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, role, provider, is_active
                FROM users 
                WHERE api_key_hash = ? AND is_active = 1
            """, (api_key_hash,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            user_id, username, email, role, provider, is_active = user_data
            
            return User(
                id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                provider=AuthProvider(provider),
                is_active=is_active,
                is_verified=True,
                has_mfa=False,
                created_at=datetime.now(timezone.utc)
            )
            
        finally:
            conn.close()
    
    def generate_jwt_tokens(self, user: User) -> AuthToken:
        """Generate JWT access and refresh tokens"""
        now = datetime.now(timezone.utc)
        
        # Access token payload
        access_payload = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "provider": user.provider.value,
            "iat": now,
            "exp": now + self.access_token_expire,
            "type": "access"
        }
        
        # Refresh token payload  
        refresh_payload = {
            "user_id": user.id,
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in database
        self._store_refresh_token(user.id, refresh_payload["jti"], now + self.refresh_token_expire)
        
        return AuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.access_token_expire.total_seconds())
        )
    
    def verify_jwt_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != token_type:
                return None
            
            # Check if refresh token is revoked
            if token_type == "refresh":
                if self._is_refresh_token_revoked(payload.get("jti")):
                    return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[AuthToken]:
        """Refresh access token using refresh token"""
        payload = self.verify_jwt_token(refresh_token, "refresh")
        if not payload:
            return None
        
        user = self.get_user_by_id(payload["user_id"])
        if not user or not user.is_active:
            return None
        
        return self.generate_jwt_tokens(user)
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke refresh token"""
        payload = self.verify_jwt_token(refresh_token, "refresh")
        if not payload:
            return False
        
        jti = payload.get("jti")
        if not jti:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE sessions 
                SET is_revoked = 1 
                WHERE refresh_token_hash = ?
            """, (hashlib.sha256(jti.encode()).hexdigest(),))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def setup_mfa(self, user_id: int) -> Tuple[str, str]:
        """Setup MFA for user, returns secret and QR code"""
        secret = pyotp.random_base32()
        
        # Update user with MFA secret
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users 
                SET mfa_secret = ?, has_mfa = 1
                WHERE id = ?
            """, (secret, user_id))
            conn.commit()
        finally:
            conn.close()
        
        # Generate QR code
        user = self.get_user_by_id(user_id)
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="Compliance Filter"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        qr_code_data = base64.b64encode(img_buffer.read()).decode()
        
        self._audit_log(user_id, "mfa_setup", True, "MFA enabled")
        
        return secret, f"data:image/png;base64,{qr_code_data}"
    
    def verify_mfa(self, user_id: int, token: str) -> bool:
        """Verify MFA token"""
        user = self.get_user_by_id(user_id)
        if not user or not user.has_mfa or not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token, valid_window=1)
    
    def get_oauth_auth_url(self, provider: str, redirect_uri: str, state: str) -> Optional[str]:
        """Get OAuth authorization URL"""
        config = self.oauth_configs.get(provider)
        if not config or not config["client_id"]:
            return None
        
        params = {
            "client_id": config["client_id"],
            "redirect_uri": redirect_uri,
            "scope": config["scope"],
            "response_type": "code",
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{config['auth_url']}?{query_string}"
    
    def exchange_oauth_code(self, provider: str, code: str, redirect_uri: str) -> Optional[User]:
        """Exchange OAuth code for user info and create/login user"""
        config = self.oauth_configs.get(provider)
        if not config:
            return None
        
        try:
            # Exchange code for access token
            token_response = requests.post(config["token_url"], data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            })
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                return None
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(config["userinfo_url"], headers=headers)
            user_data = user_response.json()
            
            # Extract user info based on provider
            if provider == "google":
                email = user_data.get("email")
                name = user_data.get("name")
                oauth_id = user_data.get("id")
            elif provider == "github":
                email = user_data.get("email")
                name = user_data.get("login")
                oauth_id = str(user_data.get("id"))
            elif provider == "microsoft":
                email = user_data.get("mail") or user_data.get("userPrincipalName")
                name = user_data.get("displayName")
                oauth_id = user_data.get("id")
            else:
                return None
            
            if not email:
                return None
            
            # Check if user exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                return existing_user
            
            # Create new OAuth user
            username = name or email.split("@")[0]
            # Ensure username is unique
            base_username = username
            counter = 1
            while self.get_user_by_username(username):
                username = f"{base_username}_{counter}"
                counter += 1
            
            return self.create_user(
                username=username,
                email=email,
                role=UserRole.VIEWER,
                provider=AuthProvider(provider),
                oauth_id=oauth_id
            )
            
        except Exception as e:
            logger.error(f"OAuth exchange error: {e}")
            return None
    
    def generate_user_api_key(self, user_id: int) -> str:
        """Generate API key for user"""
        api_key = self.generate_api_key()
        api_key_hash = self.hash_api_key(api_key)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE users 
                SET api_key_hash = ?
                WHERE id = ?
            """, (api_key_hash, user_id))
            conn.commit()
        finally:
            conn.close()
        
        self._audit_log(user_id, "api_key_generated", True, "New API key generated")
        return api_key
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, role, provider, is_active, is_verified, 
                       has_mfa, mfa_secret, created_at, last_login
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
            
            return User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                role=UserRole(user_data[3]),
                provider=AuthProvider(user_data[4]),
                is_active=user_data[5],
                is_verified=user_data[6],
                has_mfa=user_data[7],
                mfa_secret=user_data[8],
                created_at=datetime.fromisoformat(user_data[9]) if user_data[9] else datetime.now(timezone.utc),
                last_login=datetime.fromisoformat(user_data[10]) if user_data[10] else None
            )
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result:
                return self.get_user_by_id(result[0])
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id FROM users WHERE email = ?
            """, (email,))
            
            result = cursor.fetchone()
            if result:
                return self.get_user_by_id(result[0])
            return None
        finally:
            conn.close()
    
    def _store_refresh_token(self, user_id: int, jti: str, expires_at: datetime):
        """Store refresh token in database"""
        token_hash = hashlib.sha256(jti.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sessions (user_id, refresh_token_hash, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, token_hash, expires_at.isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def _is_refresh_token_revoked(self, jti: str) -> bool:
        """Check if refresh token is revoked"""
        token_hash = hashlib.sha256(jti.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT is_revoked FROM sessions 
                WHERE refresh_token_hash = ? AND expires_at > CURRENT_TIMESTAMP
            """, (token_hash,))
            
            result = cursor.fetchone()
            return result and result[0]
        finally:
            conn.close()
    
    def _audit_log(self, user_id: Optional[int], action: str, success: bool, 
                  details: str = None, ip_address: str = None, user_agent: str = None):
        """Log authentication events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO auth_audit (user_id, action, ip_address, user_agent, success, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, ip_address, user_agent, success, details))
            conn.commit()
        finally:
            conn.close()

# Flask decorators for authentication
def create_auth_decorators(auth_system: AuthSystem):
    """Create Flask authentication decorators"""
    
    def require_auth(required_role: UserRole = None):
        """Decorator to require authentication"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Check for JWT token
                auth_header = request.headers.get('Authorization')
                api_key = request.headers.get('X-API-Key')
                
                user = None
                
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    payload = auth_system.verify_jwt_token(token)
                    if payload:
                        user = auth_system.get_user_by_id(payload['user_id'])
                
                elif api_key:
                    user = auth_system.authenticate_api_key(api_key)
                
                if not user:
                    return jsonify({'error': 'Authentication required'}), 401
                
                if not user.is_active:
                    return jsonify({'error': 'Account inactive'}), 403
                
                # Check role requirement
                if required_role:
                    user_role_priority = {
                        UserRole.VIEWER: 1,
                        UserRole.ANALYST: 2, 
                        UserRole.MODERATOR: 3,
                        UserRole.ADMIN: 4
                    }
                    
                    if user_role_priority.get(user.role, 0) < user_role_priority.get(required_role, 999):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Add user to request context
                request.current_user = user
                
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_mfa():
        """Decorator to require MFA verification"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                user = getattr(request, 'current_user', None)
                if not user:
                    return jsonify({'error': 'Authentication required'}), 401
                
                if user.has_mfa:
                    mfa_token = request.headers.get('X-MFA-Token')
                    if not mfa_token or not auth_system.verify_mfa(user.id, mfa_token):
                        return jsonify({'error': 'MFA verification required'}), 403
                
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    return require_auth, require_mfa

# Helper functions
def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', '127.0.0.1')

def get_user_agent():
    """Get user agent string"""
    return request.headers.get('User-Agent', '')

if __name__ == "__main__":
    # Test the authentication system
    auth = AuthSystem()
    
    print("🔐 Testing Authentication System")
    print("=" * 40)
    
    # Test user creation
    try:
        user = auth.create_user("testuser", "test@example.com", "password123", UserRole.ANALYST)
        print(f"✅ User created: {user.username}")
        
        # Test authentication
        authenticated_user = auth.authenticate_user("testuser", "password123")
        print(f"✅ Authentication: {authenticated_user.username if authenticated_user else 'Failed'}")
        
        # Test JWT tokens
        if authenticated_user:
            tokens = auth.generate_jwt_tokens(authenticated_user)
            print(f"✅ JWT generated: {tokens.access_token[:50]}...")
            
            # Verify token
            payload = auth.verify_jwt_token(tokens.access_token)
            print(f"✅ Token verified: {payload['username'] if payload else 'Failed'}")
        
        # Test API key
        api_key = auth.generate_user_api_key(user.id)
        print(f"✅ API Key generated: {api_key}")
        
        api_user = auth.authenticate_api_key(api_key)
        print(f"✅ API Auth: {api_user.username if api_user else 'Failed'}")
        
        # Test MFA setup
        secret, qr_code = auth.setup_mfa(user.id)
        print(f"✅ MFA setup: {secret[:10]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")