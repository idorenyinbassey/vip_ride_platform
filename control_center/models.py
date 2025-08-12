"""
Control Center Models
VIP monitoring, emergency response, and security models
"""

from django.db import models
from django.conf import settings
import uuid


class IncidentType(models.TextChoices):
    SOS = 'sos', 'SOS Emergency'
    PANIC = 'panic', 'Panic Button'
    ACCIDENT = 'accident', 'Accident'
    BREAKDOWN = 'breakdown', 'Vehicle Breakdown'
    SECURITY = 'security', 'Security Threat'
    MEDICAL = 'medical', 'Medical Emergency'
    ROUTE_DEVIATION = 'route_deviation', 'Route Deviation'
    SUSPICIOUS_ACTIVITY = 'suspicious', 'Suspicious Activity'


class IncidentPriority(models.TextChoices):
    CRITICAL = 'critical', 'Critical'
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'


class IncidentStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    RESPONDED = 'responded', 'Responded'
    RESOLVED = 'resolved', 'Resolved'
    FALSE_ALARM = 'false_alarm', 'False Alarm'
    ESCALATED = 'escalated', 'Escalated'


class ResponseTeamType(models.TextChoices):
    SECURITY = 'security', 'Security Team'
    MEDICAL = 'medical', 'Medical Team'
    POLICE = 'police', 'Police'
    FIRE = 'fire', 'Fire Department'
    TECHNICAL = 'technical', 'Technical Support'


class EmergencyIncident(models.Model):
    """Emergency incident tracking for VIP users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Incident Information
    incident_type = models.CharField(
        max_length=20,
        choices=IncidentType.choices,
        default=IncidentType.SOS
    )
    priority = models.CharField(
        max_length=10,
        choices=IncidentPriority.choices,
        default=IncidentPriority.HIGH
    )
    status = models.CharField(
        max_length=15,
        choices=IncidentStatus.choices,
        default=IncidentStatus.ACTIVE
    )
    
    # User Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_incidents'
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_incidents'
    )
    
    # Ride Information
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_incidents'
    )
    vehicle = models.ForeignKey(
        'fleet_management.Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emergency_incidents'
    )
    
    # Location Information (using regular fields instead of GeoDjango)
    incident_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        help_text='Latitude of incident location'
    )
    incident_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        help_text='Longitude of incident location'
    )
    address = models.TextField(blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    
    # Incident Details
    description = models.TextField()
    automated_trigger = models.BooleanField(default=False)
    user_triggered = models.BooleanField(default=True)
    
    # Response Information
    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    response_team_type = models.CharField(
        max_length=15,
        choices=ResponseTeamType.choices,
        blank=True
    )
    response_team_contacted = models.BooleanField(default=False)
    response_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Emergency Contacts
    emergency_contacts_notified = models.BooleanField(default=False)
    police_notified = models.BooleanField(default=False)
    medical_services_notified = models.BooleanField(default=False)
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_incidents'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emergency_incidents'
        indexes = [
            models.Index(fields=['incident_type', 'priority']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['ride']),
            models.Index(fields=['created_at']),
            models.Index(fields=['assigned_operator']),
        ]
        ordering = ['-created_at', 'priority']
    
    def __str__(self):
        user_name = self.user.get_full_name()
        return f"{self.incident_type.upper()} - {user_name} - {self.created_at}"
    
    @property
    def response_time_minutes(self):
        """Calculate response time in minutes"""
        if self.response_time_seconds:
            return self.response_time_seconds / 60
        return None
    
    @property
    def is_critical(self):
        """Check if incident is critical"""
        return self.priority == IncidentPriority.CRITICAL
    
    @property
    def requires_immediate_response(self):
        """Check if incident requires immediate response"""
        critical_types = [
            IncidentType.SOS,
            IncidentType.PANIC,
            IncidentType.ACCIDENT,
            IncidentType.MEDICAL
        ]
        return (
            self.incident_type in critical_types or
            self.priority == IncidentPriority.CRITICAL
        )


class VIPMonitoringSession(models.Model):
    """Real-time monitoring session for VIP users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Session Information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='monitoring_sessions'
    )
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='vip_monitoring_sessions',
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vip_monitoring_sessions'
    )
    vehicle = models.ForeignKey(
        'fleet_management.Vehicle',
        on_delete=models.CASCADE,
        related_name='vip_monitoring_sessions',
        null=True,
        blank=True,
    )
    
    # Monitoring Details
    monitoring_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Monitoring'),
            ('enhanced', 'Enhanced Monitoring'),
            ('premium', 'Premium Monitoring'),
            ('vip', 'VIP Monitoring')
        ],
        default='basic'
    )
    
    # Assigned Operator
    assigned_operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitoring_assignments'
    )
    
    # Route Information
    planned_route = models.JSONField(default=dict)  # Store route waypoints
    current_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    route_deviation_alert = models.BooleanField(default=False)
    speed_alert = models.BooleanField(default=False)
    duration_alert = models.BooleanField(default=False)
    
    # Timestamps
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    
    # Emergency Features
    panic_button_enabled = models.BooleanField(default=True)
    auto_check_in_enabled = models.BooleanField(default=True)
    check_in_interval_minutes = models.PositiveIntegerField(default=15)
    last_check_in = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vip_monitoring_sessions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['ride']),
            models.Index(fields=['is_active']),
            models.Index(fields=['assigned_operator']),
            models.Index(fields=['session_start']),
        ]
    
    def __str__(self):
        name = self.user.get_full_name()
        return f"VIP Monitor - {name} - {self.session_start}"
    
    @property
    def is_overdue_checkin(self):
        """Check if user is overdue for check-in"""
        if not self.auto_check_in_enabled or not self.last_check_in:
            return False
        
        from datetime import timedelta
        from django.utils import timezone
        
        overdue_threshold = (
            self.last_check_in +
            timedelta(minutes=self.check_in_interval_minutes + 5)
        )
        return timezone.now() > overdue_threshold


class ControlOperator(models.Model):
    """Control center operator profiles"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='control_operator'
    )
    
    # Operator Information
    operator_id = models.CharField(max_length=20, unique=True)
    security_clearance_level = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic'),
            ('enhanced', 'Enhanced'),
            ('vip', 'VIP'),
            ('supervisor', 'Supervisor')
        ],
        default='basic'
    )
    
    # Capabilities
    can_handle_emergencies = models.BooleanField(default=True)
    can_contact_authorities = models.BooleanField(default=False)
    can_escalate_incidents = models.BooleanField(default=True)
    can_monitor_vip = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_on_duty = models.BooleanField(default=False)
    current_shift_start = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    total_incidents_handled = models.PositiveIntegerField(default=0)
    average_response_time_seconds = models.PositiveIntegerField(default=0)
    successful_resolutions = models.PositiveIntegerField(default=0)
    
    # Emergency Contacts
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_operators'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'control_operators'
        indexes = [
            models.Index(fields=['operator_id']),
            models.Index(fields=['security_clearance_level']),
            models.Index(fields=['is_active', 'is_on_duty']),
        ]
    
    def __str__(self):
        return f"Operator {self.operator_id} - {self.user.get_full_name()}"


class IncidentResponse(models.Model):
    """Incident response actions and timeline"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    incident = models.ForeignKey(
        EmergencyIncident,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Response Details
    action_type = models.CharField(
        max_length=30,
        choices=[
            ('initial_contact', 'Initial Contact'),
            ('status_update', 'Status Update'),
            ('authority_contact', 'Authority Contacted'),
            ('team_dispatch', 'Team Dispatched'),
            ('escalation', 'Escalated'),
            ('resolution', 'Resolved'),
            ('follow_up', 'Follow-up')
        ]
    )
    
    description = models.TextField()
    operator = models.ForeignKey(
        ControlOperator,
        on_delete=models.CASCADE,
        related_name='incident_responses'
    )
    
    # Authority Information
    authority_contacted = models.CharField(
        max_length=50,
        blank=True,
        help_text='Police, Medical, Fire, etc.'
    )
    authority_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference number from authority'
    )
    
    # Response Team
    team_dispatched = models.CharField(max_length=100, blank=True)
    estimated_arrival_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'incident_responses'
        indexes = [
            models.Index(fields=['incident']),
            models.Index(fields=['action_type']),
            models.Index(fields=['operator']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.incident.id} - {self.created_at}"


class SOSConfiguration(models.Model):
    """SOS system configuration for different user tiers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Configuration Details
    user_tier = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'Normal'),
            ('premium', 'Premium'),
            ('vip', 'VIP')
        ],
        unique=True
    )
    
    # Response Configuration
    auto_response_enabled = models.BooleanField(default=True)
    max_response_time_seconds = models.PositiveIntegerField(default=300)  # 5 minutes
    escalation_time_seconds = models.PositiveIntegerField(default=600)  # 10 minutes
    
    # Authority Contact
    auto_contact_police = models.BooleanField(default=False)
    auto_contact_medical = models.BooleanField(default=False)
    requires_supervisor_approval = models.BooleanField(default=False)
    
    # Monitoring Features
    real_time_monitoring = models.BooleanField(default=False)
    gps_tracking_frequency_seconds = models.PositiveIntegerField(default=60)
    route_deviation_alert = models.BooleanField(default=False)
    
    # Emergency Contacts
    notify_emergency_contacts = models.BooleanField(default=True)
    max_emergency_contacts = models.PositiveIntegerField(default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sos_configurations'
    
    def __str__(self):
        return f"SOS Config - {self.user_tier.upper()}"
