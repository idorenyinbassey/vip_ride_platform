import 'package:flutter/material.dart';
import '../../models/ride_models.dart';

class VehicleSelector extends StatelessWidget {
  final String selectedVehicleType;
  final Function(String) onVehicleTypeChanged;
  final List<Driver> nearbyDrivers;

  const VehicleSelector({
    super.key,
    required this.selectedVehicleType,
    required this.onVehicleTypeChanged,
    required this.nearbyDrivers,
  });

  @override
  Widget build(BuildContext context) {
    final vehicleTypes = [
      {
        'type': 'economy',
        'name': 'Economy',
        'icon': Icons.directions_car,
        'description': 'Affordable rides',
        'eta': _getEtaForVehicleType('economy'),
      },
      {
        'type': 'standard',
        'name': 'Standard',
        'icon': Icons.local_taxi,
        'description': 'Comfortable rides',
        'eta': _getEtaForVehicleType('standard'),
      },
      {
        'type': 'premium',
        'name': 'Premium',
        'icon': Icons.car_rental,
        'description': 'Luxury vehicles',
        'eta': _getEtaForVehicleType('premium'),
      },
      {
        'type': 'suv',
        'name': 'SUV',
        'icon': Icons.airport_shuttle,
        'description': 'Extra space',
        'eta': _getEtaForVehicleType('suv'),
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Choose Vehicle',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        SizedBox(
          height: 100,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: vehicleTypes.length,
            itemBuilder: (context, index) {
              final vehicle = vehicleTypes[index];
              final isSelected = selectedVehicleType == vehicle['type'];

              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: GestureDetector(
                  onTap: () => onVehicleTypeChanged(vehicle['type'] as String),
                  child: Container(
                    width: 120,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isSelected ? Colors.blue[50] : Colors.grey[100],
                      border: Border.all(
                        color: isSelected ? Colors.blue : Colors.grey[300]!,
                        width: isSelected ? 2 : 1,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          vehicle['icon'] as IconData,
                          size: 28,
                          color: isSelected ? Colors.blue : Colors.grey[700],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          vehicle['name'] as String,
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: isSelected ? Colors.blue : Colors.grey[700],
                            fontSize: 12,
                          ),
                        ),
                        Text(
                          vehicle['description'] as String,
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.grey[600],
                          ),
                        ),
                        if (vehicle['eta'] != null)
                          Text(
                            '${vehicle['eta']} min',
                            style: TextStyle(
                              fontSize: 10,
                              color: isSelected
                                  ? Colors.blue
                                  : Colors.grey[600],
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  int? _getEtaForVehicleType(String vehicleType) {
    final drivers = nearbyDrivers
        .where(
          (driver) =>
              driver.vehicleType.toLowerCase() == vehicleType.toLowerCase(),
        )
        .toList();

    if (drivers.isEmpty) return null;

    // Return the ETA of the closest driver
    drivers.sort((a, b) => a.distance.compareTo(b.distance));
    return drivers.first.eta;
  }
}
