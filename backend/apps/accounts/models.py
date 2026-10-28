import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    headline = models.CharField(max_length=255, blank=True, default='')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.email.split('@')[0]

    def __str__(self):
        return self.email

class Organization(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('INACTIVE', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    logo_url = models.URLField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']

    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ('PLATFORM_ADMIN', 'Platform Administrator'),
        ('ORG_ADMIN', 'Organization Administrator'),
        ('INSTRUCTOR', 'Instructor'),
        ('STUDENT', 'Student'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PENDING_INVITE', 'Pending Invite'),
        ('REVOKED', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='STUDENT')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organization_memberships'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'user'], name='unique_org_user_membership')
        ]
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.email} - {self.organization.slug} ({self.role})"

class Invitation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=30, choices=OrganizationMembership.ROLE_CHOICES, default='STUDENT')
    token = models.CharField(max_length=128, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invitations'
        ordering = ['-created_at']

    def is_valid(self):
        return self.status == 'PENDING' and self.expires_at > timezone.now()

    def __str__(self):
        return f"Invite {self.email} to {self.organization.name} as {self.role}"
