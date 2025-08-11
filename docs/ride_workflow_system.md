# VIP Ride-Hailing Platform - Ride Status Workflow System

## 📋 Overview

The Ride Status Workflow System is a comprehensive state machine that manages the entire lifecycle of rides from request to completion. It includes automatic transitions, tier-based policies, payment integration, and emergency protocols.

## 🔄 State Machine Architecture

### Core Status Flow
```
REQUESTED → DRIVER_SEARCH → DRIVER_FOUND → DRIVER_ACCEPTED → 
DRIVER_EN_ROUTE → DRIVER_ARRIVED → IN_PROGRESS → COMPLETED → 
PAYMENT_PENDING → PAYMENT_COMPLETED
```

### Complete State Diagram
```
REQUESTED
├── DRIVER_SEARCH
│   ├── DRIVER_FOUND
│   │   ├── DRIVER_ACCEPTED → DRIVER_EN_ROUTE → DRIVER_ARRIVED → IN_PROGRESS
│   │   ├── DRIVER_REJECTED → DRIVER_SEARCH (retry)
│   │   └── CANCELLED_BY_RIDER
│   └── CANCELLED_BY_RIDER/SYSTEM
├── CANCELLED_BY_RIDER
└── CANCELLED_BY_SYSTEM

IN_PROGRESS
├── COMPLETED → PAYMENT_PENDING
│   ├── PAYMENT_COMPLETED (final)
│   └── PAYMENT_FAILED → PAYMENT_PENDING (retry)
├── CANCELLED_BY_DRIVER
└── DISPUTED → REFUNDED

Terminal States: CANCELLED_*, PAYMENT_COMPLETED, REFUNDED
```

## 🏗️ Core Components

### 1. RideWorkflow Class
- **Purpose**: State machine for individual rides
- **Key Methods**:
  - `can_transition_to(status)`: Validates transitions
  - `transition_to(status, user, reason)`: Executes transitions
  - `_trigger_status_actions(status)`: Automatic actions

### 2. RideWorkflowManager Class
- **Purpose**: High-level workflow operations
- **Key Methods**:
  - `request_ride()`: Create and start workflow
  - `driver_accept_ride()`: Handle driver acceptance
  - `cancel_ride()`: Process cancellations with policies
  - `complete_ride()`: Handle ride completion

### 3. CancellationPolicy Class
- **Purpose**: Tier-based cancellation rules
- **Policies by Tier**:
  ```python
  'normal': {
      'free_cancellation_window': 300,  # 5 minutes
      'max_cancellations_per_day': 3,
      'driver_acceptance_timeout': 180  # 3 minutes
  },
  'premium': {
      'free_cancellation_window': 600,  # 10 minutes
      'max_cancellations_per_day': 5,
      'driver_acceptance_timeout': 120  # 2 minutes
  },
  'vip': {
      'free_cancellation_window': 900,  # 15 minutes
      'max_cancellations_per_day': 10,
      'driver_acceptance_timeout': 60   # 1 minute
  }
  ```

## 📊 Database Models

### Core Models
- **Ride**: Enhanced with workflow fields
- **RideStatusHistory**: Tracks all status changes
- **WorkflowAction**: Manages background actions
- **CancellationRecord**: Detailed cancellation tracking
- **PaymentWorkflow**: Payment processing steps
- **RideCompletionWorkflow**: Completion confirmation

### Key Fields Added to Ride Model
```python
# Workflow timing fields
driver_accepted_at = models.DateTimeField(null=True)
driver_en_route_at = models.DateTimeField(null=True)
driver_arrived_at = models.DateTimeField(null=True)
started_at = models.DateTimeField(null=True)
completed_at = models.DateTimeField(null=True)
cancelled_at = models.DateTimeField(null=True)

# Workflow control
workflow_step = models.CharField(max_length=50)
auto_transitions_enabled = models.BooleanField(default=True)
```

## 🔧 API Endpoints

### Ride Lifecycle Endpoints
```
POST   /api/v1/rides/workflow/request/              # Create ride request
POST   /api/v1/rides/workflow/{id}/accept/          # Driver accepts
DELETE /api/v1/rides/workflow/{id}/accept/          # Driver rejects
POST   /api/v1/rides/workflow/{id}/cancel/          # Cancel ride
PATCH  /api/v1/rides/workflow/{id}/status/          # Update status
POST   /api/v1/rides/workflow/{id}/complete/        # Complete ride
```

### Information Endpoints
```
GET    /api/v1/rides/workflow/active/               # User's active rides
GET    /api/v1/rides/workflow/{id}/history/         # Status history
GET    /api/v1/rides/workflow/{id}/workflow/        # Workflow details
GET    /api/v1/rides/workflow/cancellation-policy/ # Policy info
```

### Emergency Endpoints
```
POST   /api/v1/rides/workflow/{id}/sos/             # Trigger SOS (VIP only)
```

## 🚗 Driver Interaction Flow

### 1. Driver Assignment
```python
# System finds available drivers
workflow.transition_to(RideStatus.DRIVER_SEARCH)

# Driver is assigned to ride
workflow.transition_to(RideStatus.DRIVER_FOUND)
# → Notification sent to driver

# Driver has limited time to respond based on user tier
# VIP: 60 seconds, Premium: 120 seconds, Normal: 180 seconds
```

### 2. Driver Acceptance
```python
# Driver accepts
RideWorkflowManager.driver_accept_ride(ride, driver_user)
# → Status: DRIVER_ACCEPTED
# → Auto-transition to DRIVER_EN_ROUTE
# → Rider notification sent

# Driver rejects
RideWorkflowManager.driver_reject_ride(ride, driver_user, reason)
# → Status: DRIVER_REJECTED
# → Auto-transition back to DRIVER_SEARCH
```

### 3. Pickup Process
```python
# Driver updates status as they approach
workflow.transition_to(RideStatus.DRIVER_ARRIVED)
# → Rider notified
# → GPS tracking intensified

# Driver starts ride
workflow.transition_to(RideStatus.IN_PROGRESS)
# → Real-time tracking begins
# → Route recording starts
```

## 💳 Payment Integration

### Payment Workflow States
```
COMPLETED → PAYMENT_PENDING → PAYMENT_COMPLETED
                ↓
           PAYMENT_FAILED → PAYMENT_PENDING (retry)
```

### Payment Processing
```python
# Automatic payment initiation on completion
def _initiate_payment(self):
    payment_service = PaymentService()
    transaction = payment_service.create_ride_payment(self.ride)
    
    if transaction:
        self.transition_to(RideStatus.PAYMENT_PENDING)
    else:
        self.transition_to(RideStatus.PAYMENT_FAILED)
```

### Commission Calculation
```python
def calculate_final_fare(self):
    calculated_fare = self.calculate_flexible_fare()
    commission_rate = float(self.platform_commission_rate) / 100
    
    self.platform_commission = calculated_fare * commission_rate
    self.driver_earnings = calculated_fare - self.platform_commission
    
    # Fleet company cut if applicable
    if self.fleet_company:
        fleet_rate = float(self.fleet_company.commission_rate) / 100
        self.fleet_commission = calculated_fare * fleet_rate
        self.driver_earnings -= self.fleet_commission
```

## 🚨 Emergency Features

### SOS Trigger (VIP Only)
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVIPUser])
def trigger_sos(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Trigger emergency protocol
    ride.trigger_sos()
    
    # Create workflow action for processing
    WorkflowAction.objects.create(
        ride=ride,
        action_type=WorkflowAction.ActionType.SOS_TRIGGER,
        action_data={
            'emergency_type': request.data.get('emergency_type'),
            'location_override': request.data.get('location_override')
        }
    )
```

### Emergency Response Chain
1. **Immediate**: GPS encryption activated, location shared
2. **5 seconds**: Control center alerted
3. **30 seconds**: Emergency contacts notified
4. **60 seconds**: Local emergency services contacted
5. **Ongoing**: Real-time monitoring activated

## ⚙️ Background Processing

### Automatic Actions
Each status transition can trigger automatic actions:

```python
DRIVER_SEARCH → Start driver matching algorithm
DRIVER_FOUND → Send driver notification
DRIVER_ACCEPTED → Notify rider, start ETA tracking
DRIVER_EN_ROUTE → Enable real-time tracking
IN_PROGRESS → Start route recording, activate GPS encryption
COMPLETED → Calculate fare, initiate payment
PAYMENT_COMPLETED → Finalize ride, update driver earnings
```

### WorkflowAction Processing
```bash
# Run via cron job or Celery
python manage.py process_workflow_actions --max-actions=100

# Process specific action types
python manage.py process_workflow_actions --action-type=payment_process

# Dry run to see what would be processed
python manage.py process_workflow_actions --dry-run
```

## 🔒 Security Features

### VIP Protections
- **GPS Encryption**: AES-256-GCM for location data
- **SOS Integration**: Direct emergency service connection
- **Enhanced Monitoring**: Control center oversight
- **Trusted Drivers**: VIP-verified driver pool

### Data Protection
- **Audit Trail**: Complete status history logging
- **NDPR Compliance**: Data anonymization
- **Access Control**: Role-based permissions
- **Secure Storage**: Encrypted sensitive data

## 📈 Analytics & Monitoring

### Workflow Metrics
- **Status Duration**: Time spent in each status
- **Transition Success Rate**: Failed vs successful transitions
- **Cancellation Analysis**: Patterns by tier and timing
- **Payment Success Rate**: Processing efficiency
- **Driver Response Time**: Acceptance/rejection speed

### Performance Monitoring
```python
# Get workflow performance data
from rides.workflow import get_rides_by_status

pending_payments = get_rides_by_status(RideStatus.PAYMENT_PENDING)
failed_payments = get_rides_by_status(RideStatus.PAYMENT_FAILED)

# Calculate success rates
success_rate = len(completed) / (len(completed) + len(failed)) * 100
```

## 🧪 Testing

### Test Categories
1. **Unit Tests**: Individual workflow components
2. **Integration Tests**: Complete ride workflows
3. **API Tests**: Endpoint functionality
4. **Policy Tests**: Cancellation and tier rules
5. **Security Tests**: Authorization and data protection

### Running Tests
```bash
# Run all workflow tests
python manage.py test rides.test_workflow

# Run specific test categories
python manage.py test rides.test_workflow.RideWorkflowTestCase
python manage.py test rides.test_workflow.CancellationPolicyTestCase
python manage.py test rides.test_workflow.WorkflowAPITestCase
```

## 🚀 Deployment Considerations

### Production Setup
1. **Background Processing**: Set up Celery workers
2. **Real-time Updates**: Configure WebSocket support
3. **Payment Gateway**: Integrate Paystack/Stripe
4. **Monitoring**: Set up error tracking (Sentry)
5. **Performance**: Redis caching for workflow states

### Scaling Considerations
- **Database Indexing**: Optimize for status queries
- **Queue Management**: Separate queues for critical actions
- **Caching Strategy**: Cache policy calculations
- **Load Balancing**: Distribute workflow processing

## 📝 Usage Examples

### Creating a Ride Request
```python
from rides.workflow import RideWorkflowManager

ride = RideWorkflowManager.request_ride(
    rider=user,
    pickup_location={
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'New York, NY'
    },
    destination_location={
        'latitude': 40.7589,
        'longitude': -73.9851,
        'address': 'Times Square, NY'
    },
    ride_type='vip'
)
```

### Driver Workflow
```python
# Driver accepts ride
success = RideWorkflowManager.driver_accept_ride(ride, driver_user)

# Update status as driver progresses
workflow = RideWorkflow(ride)
workflow.transition_to(RideStatus.DRIVER_ARRIVED, user=driver_user)
workflow.transition_to(RideStatus.IN_PROGRESS, user=driver_user)

# Complete ride
RideWorkflowManager.complete_ride(ride, driver_user)
```

### Cancellation with Policy Check
```python
# Check if user can cancel
can_cancel, message = CancellationPolicy.can_cancel_free(ride, 'premium')

if can_cancel:
    success, result = RideWorkflowManager.cancel_ride(
        ride=ride,
        user=rider,
        reason='Plans changed'
    )
```

## 🔍 Troubleshooting

### Common Issues
1. **Invalid Transitions**: Check current status and valid next states
2. **Policy Violations**: Verify tier limits and time windows
3. **Payment Failures**: Check gateway configuration and retry logic
4. **Action Timeouts**: Monitor background processing and queues

### Debug Tools
```python
# Check workflow status
workflow = RideWorkflow(ride)
print(f"Current: {workflow.current_status}")
print(f"Can transition to completed: {workflow.can_transition_to(RideStatus.COMPLETED)}")

# View recent actions
recent_actions = ride.workflow_actions.filter(
    created_at__gte=timezone.now() - timedelta(hours=1)
)
for action in recent_actions:
    print(f"{action.action_type}: {action.action_status}")
```

---

This comprehensive workflow system ensures reliable, secure, and efficient ride management with proper state transitions, policy enforcement, and emergency protocols for the VIP ride-hailing platform.
