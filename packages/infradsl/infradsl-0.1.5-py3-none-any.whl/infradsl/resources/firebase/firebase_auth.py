from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class AuthProvider(Enum):
    """Firebase Auth providers"""
    EMAIL_PASSWORD = "password"
    GOOGLE = "google.com"
    FACEBOOK = "facebook.com"
    TWITTER = "twitter.com"
    GITHUB = "github.com"
    APPLE = "apple.com"
    MICROSOFT = "microsoft.com"
    PHONE = "phone"
    ANONYMOUS = "anonymous"


@dataclass
class OAuthConfig:
    """OAuth provider configuration"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    enabled: bool = True


@dataclass
class EmailConfig:
    """Email provider configuration"""
    enabled: bool = True
    password_required: bool = True
    email_link_signin: bool = False


@dataclass
class PhoneConfig:
    """Phone authentication configuration"""
    enabled: bool = True
    test_phone_numbers: Dict[str, str] = field(default_factory=dict)


@dataclass
class FirebaseAuthSpec(ResourceSpec):
    """Specification for Firebase Authentication"""
    
    # Project configuration
    project_id: Optional[str] = None
    
    # Sign-in methods
    email_config: EmailConfig = field(default_factory=EmailConfig)
    phone_config: PhoneConfig = field(default_factory=PhoneConfig)
    anonymous_enabled: bool = False
    
    # OAuth providers
    oauth_providers: Dict[str, OAuthConfig] = field(default_factory=dict)
    
    # Security settings
    enforce_domain_restrictions: bool = False
    authorized_domains: List[str] = field(default_factory=list)
    
    # Password policy
    min_password_length: int = 6
    require_uppercase: bool = False
    require_lowercase: bool = False
    require_numeric: bool = False
    require_special_char: bool = False
    
    # MFA settings
    mfa_enabled: bool = False
    mfa_enrollment: str = "optional"  # optional, required, disabled
    
    # Session management
    session_timeout_minutes: int = 60
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class FirebaseAuth(BaseResource):
    """
    Firebase Authentication service with Rails-like conventions.
    
    Examples:
        # Basic email/password authentication
        auth = (FirebaseAuth("myapp-auth")
                .email_password()
                .authorized_domain("myapp.com")
                .authorized_domain("staging.myapp.com"))
        
        # Social authentication
        social_auth = (FirebaseAuth("social-auth")
                      .email_password()
                      .google_signin("client-id", "client-secret")
                      .github_signin("github-client-id", "github-secret")
                      .facebook_signin("fb-app-id", "fb-secret")
                      .anonymous_signin())
        
        # Production authentication with MFA
        prod_auth = (FirebaseAuth("prod-auth")
                    .email_password()
                    .phone_authentication()
                    .google_signin("prod-client-id", "prod-secret")
                    .strong_password_policy()
                    .mfa_required()
                    .authorized_domains(["myapp.com", "www.myapp.com"])
                    .production())
        
        # Development authentication (permissive)
        dev_auth = (FirebaseAuth("dev-auth")
                   .email_password()
                   .anonymous_signin()
                   .test_phone_numbers({"+1555": "123456"})
                   .development())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: FirebaseAuthSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "FirebaseAuth"
        
    def _create_spec(self) -> FirebaseAuthSpec:
        return FirebaseAuthSpec()
        
    def _validate_spec(self) -> None:
        """Validate authentication specification"""
        if not any([
            self.spec.email_config.enabled,
            self.spec.phone_config.enabled,
            self.spec.anonymous_enabled,
            bool(self.spec.oauth_providers)
        ]):
            raise ValueError("At least one sign-in method must be enabled")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "project_id": self.spec.project_id or self.metadata.name,
            "sign_in": self._build_signin_config(),
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config
        
    def _build_signin_config(self) -> Dict[str, Any]:
        """Build sign-in methods configuration"""
        signin_methods = []
        
        # Email/password
        if self.spec.email_config.enabled:
            email_method = {
                "providerId": "password",
                "enabled": True
            }
            if self.spec.email_config.email_link_signin:
                email_method["emailLinkSignin"] = True
            signin_methods.append(email_method)
            
        # Phone authentication
        if self.spec.phone_config.enabled:
            phone_method = {
                "providerId": "phone",
                "enabled": True
            }
            if self.spec.phone_config.test_phone_numbers:
                phone_method["testPhoneNumbers"] = self.spec.phone_config.test_phone_numbers
            signin_methods.append(phone_method)
            
        # Anonymous
        if self.spec.anonymous_enabled:
            signin_methods.append({
                "providerId": "anonymous",
                "enabled": True
            })
            
        # OAuth providers
        for provider_id, config in self.spec.oauth_providers.items():
            oauth_method = {
                "providerId": provider_id,
                "enabled": config.enabled
            }
            if config.client_id:
                oauth_method["clientId"] = config.client_id
            if config.client_secret:
                oauth_method["clientSecret"] = config.client_secret
            signin_methods.append(oauth_method)
            
        return {"methods": signin_methods}

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to Firebase configuration"""
        config = {
            "resource_type": "firebase_project"
        }
        
        # Authorized domains
        if self.spec.authorized_domains:
            config["authorized_domains"] = self.spec.authorized_domains
            
        # Password policy
        if any([
            self.spec.min_password_length != 6,
            self.spec.require_uppercase,
            self.spec.require_lowercase, 
            self.spec.require_numeric,
            self.spec.require_special_char
        ]):
            password_policy = {
                "minLength": self.spec.min_password_length
            }
            
            constraints = []
            if self.spec.require_uppercase:
                constraints.append("REQUIRE_UPPERCASE")
            if self.spec.require_lowercase:
                constraints.append("REQUIRE_LOWERCASE")
            if self.spec.require_numeric:
                constraints.append("REQUIRE_NUMERIC")
            if self.spec.require_special_char:
                constraints.append("REQUIRE_NON_ALPHANUMERIC")
                
            if constraints:
                password_policy["constraints"] = constraints
                
            config["password_policy"] = password_policy
            
        # MFA configuration
        if self.spec.mfa_enabled:
            config["mfa_config"] = {
                "state": "ENABLED",
                "enrollment": self.spec.mfa_enrollment.upper()
            }
            
        return config
        
    # Fluent interface methods
    
    # Basic authentication methods
    
    def email_password(self, email_link: bool = False) -> Self:
        """Enable email/password authentication (chainable)"""
        self.spec.email_config.enabled = True
        self.spec.email_config.email_link_signin = email_link
        return self
        
    def phone_authentication(self) -> Self:
        """Enable phone authentication (chainable)"""
        self.spec.phone_config.enabled = True
        return self
        
    def anonymous_signin(self) -> Self:
        """Enable anonymous authentication (chainable)"""
        self.spec.anonymous_enabled = True
        return self
        
    # OAuth providers
    
    def google_signin(self, client_id: str, client_secret: str = None) -> Self:
        """Enable Google Sign-In (chainable)"""
        self.spec.oauth_providers[AuthProvider.GOOGLE.value] = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            enabled=True
        )
        return self
        
    def facebook_signin(self, app_id: str, app_secret: str) -> Self:
        """Enable Facebook Login (chainable)"""
        self.spec.oauth_providers[AuthProvider.FACEBOOK.value] = OAuthConfig(
            client_id=app_id,
            client_secret=app_secret,
            enabled=True
        )
        return self
        
    def github_signin(self, client_id: str, client_secret: str) -> Self:
        """Enable GitHub authentication (chainable)"""
        self.spec.oauth_providers[AuthProvider.GITHUB.value] = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            enabled=True
        )
        return self
        
    def twitter_signin(self, api_key: str, api_secret: str) -> Self:
        """Enable Twitter authentication (chainable)"""
        self.spec.oauth_providers[AuthProvider.TWITTER.value] = OAuthConfig(
            client_id=api_key,
            client_secret=api_secret,
            enabled=True
        )
        return self
        
    def apple_signin(self, service_id: str, team_id: str = None, key_id: str = None) -> Self:
        """Enable Sign in with Apple (chainable)"""
        self.spec.oauth_providers[AuthProvider.APPLE.value] = OAuthConfig(
            client_id=service_id,
            enabled=True
        )
        return self
        
    def microsoft_signin(self, client_id: str, client_secret: str) -> Self:
        """Enable Microsoft authentication (chainable)"""
        self.spec.oauth_providers[AuthProvider.MICROSOFT.value] = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            enabled=True
        )
        return self
        
    # Domain and security configuration
    
    def authorized_domain(self, domain: str) -> Self:
        """Add authorized domain (chainable)"""
        if domain not in self.spec.authorized_domains:
            self.spec.authorized_domains.append(domain)
        return self
        
    def authorized_domains(self, domains: List[str]) -> Self:
        """Set authorized domains (chainable)"""
        self.spec.authorized_domains = domains.copy()
        return self
        
    def enforce_domain_restrictions(self, enabled: bool = True) -> Self:
        """Enforce domain restrictions (chainable)"""
        self.spec.enforce_domain_restrictions = enabled
        return self
        
    # Password policy
    
    def password_policy(self, min_length: int = 6, uppercase: bool = False, 
                       lowercase: bool = False, numeric: bool = False, 
                       special_char: bool = False) -> Self:
        """Configure password policy (chainable)"""
        self.spec.min_password_length = min_length
        self.spec.require_uppercase = uppercase
        self.spec.require_lowercase = lowercase
        self.spec.require_numeric = numeric
        self.spec.require_special_char = special_char
        return self
        
    def weak_password_policy(self) -> Self:
        """Use weak password policy (chainable)"""
        return self.password_policy(min_length=4)
        
    def strong_password_policy(self) -> Self:
        """Use strong password policy (chainable)"""
        return self.password_policy(
            min_length=8, 
            uppercase=True, 
            lowercase=True, 
            numeric=True, 
            special_char=True
        )
        
    # MFA configuration
    
    def mfa_optional(self) -> Self:
        """Enable optional MFA (chainable)"""
        self.spec.mfa_enabled = True
        self.spec.mfa_enrollment = "optional"
        return self
        
    def mfa_required(self) -> Self:
        """Require MFA for all users (chainable)"""
        self.spec.mfa_enabled = True
        self.spec.mfa_enrollment = "required"
        return self
        
    def mfa_disabled(self) -> Self:
        """Disable MFA (chainable)"""
        self.spec.mfa_enabled = False
        return self
        
    # Testing helpers
    
    def test_phone_number(self, phone: str, verification_code: str) -> Self:
        """Add test phone number (chainable)"""
        self.spec.phone_config.test_phone_numbers[phone] = verification_code
        return self
        
    def test_phone_numbers(self, phone_codes: Dict[str, str]) -> Self:
        """Set test phone numbers (chainable)"""
        self.spec.phone_config.test_phone_numbers.update(phone_codes)
        return self
        
    # Session management
    
    def session_timeout(self, minutes: int) -> Self:
        """Set session timeout (chainable)"""
        self.spec.session_timeout_minutes = minutes
        return self
        
    # Labels
    
    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.labels[key] = value
        return self
        
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.labels.update(labels_dict)
        if labels:
            self.spec.labels.update(labels)
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .strong_password_policy()
                .mfa_optional()
                .session_timeout(720)  # 12 hours
                .enforce_domain_restrictions()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .password_policy(min_length=6)
                .session_timeout(480)  # 8 hours
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .weak_password_policy()
                .anonymous_signin()
                .test_phone_numbers({
                    "+15551234567": "123456",
                    "+15559876543": "654321"
                })
                .session_timeout(1440)  # 24 hours
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the Firebase Auth configuration via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the Firebase Auth configuration via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the Firebase Auth configuration via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )
        
    # Convenience methods
    
    def get_project_id(self) -> str:
        """Get Firebase project ID"""
        return self.spec.project_id or self.metadata.name
        
    def get_auth_domain(self) -> str:
        """Get Firebase Auth domain"""
        project_id = self.get_project_id()
        return f"{project_id}.firebaseapp.com"