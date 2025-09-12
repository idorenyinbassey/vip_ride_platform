import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../models/ride_models.dart';

class RideBookingSheet extends StatelessWidget {
  final Ride ride;
  final VoidCallback onCancelRide;
  final VoidCallback onSOSPressed;

  const RideBookingSheet({
    super.key,
    required this.ride,
    required this.onCancelRide,
    required this.onSOSPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 16),

          // Ride status
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _getStatusColor(ride.status),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              children: [
                Text(
                  _getStatusText(ride.status),
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                if (ride.hasDriver) ...[
                  const SizedBox(height: 8),
                  Text(
                    _getStatusDescription(ride.status),
                    style: const TextStyle(fontSize: 14, color: Colors.white70),
                    textAlign: TextAlign.center,
                  ),
                ],
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Driver info (if assigned)
          if (ride.hasDriver) ...[
            _buildDriverInfo(),
            const SizedBox(height: 16),
          ],

          // Ride details
          _buildRideDetails(),

          const Spacer(),

          // Action buttons
          _buildActionButtons(context),
        ],
      ),
    );
  }

  Widget _buildDriverInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          // Driver avatar
          CircleAvatar(
            radius: 30,
            backgroundColor: Colors.blue[100],
            child: Text(
              ride.driverName?.substring(0, 1).toUpperCase() ?? 'D',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.blue[700],
              ),
            ),
          ),

          const SizedBox(width: 16),

          // Driver details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  ride.driverName ?? 'Driver',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (ride.driverRating != null)
                  Row(
                    children: [
                      Icon(Icons.star, size: 16, color: Colors.amber[600]),
                      const SizedBox(width: 4),
                      Text(
                        ride.driverRating!.toStringAsFixed(1),
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                if (ride.vehicleModel != null || ride.vehiclePlate != null)
                  Text(
                    '${ride.vehicleModel ?? ''} • ${ride.vehiclePlate ?? ''}',
                    style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                  ),
              ],
            ),
          ),

          // Call button
          if (ride.driverPhone != null)
            IconButton(
              onPressed: () => _callDriver(ride.driverPhone!),
              icon: const Icon(Icons.phone),
              style: IconButton.styleFrom(
                backgroundColor: Colors.green[100],
                foregroundColor: Colors.green[700],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildRideDetails() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          // Pickup
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: const BoxDecoration(
                  color: Colors.green,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Pickup',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      ride.pickup.address,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          // Connecting line
          Container(
            margin: const EdgeInsets.only(left: 6, top: 8, bottom: 8),
            height: 20,
            width: 2,
            color: Colors.grey[300],
          ),

          // Destination
          Row(
            children: [
              Container(
                width: 12,
                height: 12,
                decoration: const BoxDecoration(
                  color: Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Destination',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Text(
                      ride.destination.address,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          if (ride.fare != null || ride.estimatedFare != null) ...[
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Fare',
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
                Text(
                  'NGN ${(ride.fare ?? ride.estimatedFare)!.toStringAsFixed(0)}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context) {
    return Row(
      children: [
        // SOS button (for VIP users)
        if (ride.serviceLevel == 'vip' ||
            ride.serviceLevel == 'vip_premium') ...[
          Expanded(
            child: ElevatedButton(
              onPressed: onSOSPressed,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.emergency, size: 20),
                  SizedBox(width: 8),
                  Text('SOS'),
                ],
              ),
            ),
          ),
          const SizedBox(width: 12),
        ],

        // Cancel button
        Expanded(
          flex: ride.serviceLevel == 'vip' || ride.serviceLevel == 'vip_premium'
              ? 2
              : 1,
          child: ElevatedButton(
            onPressed: _canCancelRide() ? onCancelRide : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[600],
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
            child: const Text('Cancel Ride'),
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'accepted':
      case 'driver_assigned':
        return Colors.blue;
      case 'driver_arriving':
      case 'in_progress':
        return Colors.green;
      case 'completed':
        return Colors.purple;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Finding Driver...';
      case 'accepted':
      case 'driver_assigned':
        return 'Driver Assigned';
      case 'driver_arriving':
        return 'Driver Arriving';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Ride Completed';
      case 'cancelled':
        return 'Ride Cancelled';
      default:
        return status.toUpperCase();
    }
  }

  String _getStatusDescription(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'We\'re finding the best driver for you';
      case 'accepted':
      case 'driver_assigned':
        return 'Your driver is on the way to pick you up';
      case 'driver_arriving':
        return 'Your driver will arrive shortly';
      case 'in_progress':
        return 'Enjoy your ride!';
      case 'completed':
        return 'Thank you for choosing us';
      case 'cancelled':
        return 'This ride has been cancelled';
      default:
        return '';
    }
  }

  bool _canCancelRide() {
    return [
      'pending',
      'accepted',
      'driver_assigned',
      'driver_arriving',
    ].contains(ride.status.toLowerCase());
  }

  void _callDriver(String phoneNumber) async {
    final uri = Uri.parse('tel:$phoneNumber');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }
}
