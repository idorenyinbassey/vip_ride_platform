import 'package:flutter/material.dart';
import '../../models/ride_models.dart';
import '../../services/ride_service.dart';

class LocationInput extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final IconData icon;
  final Function(LocationData) onLocationSelected;

  const LocationInput({
    super.key,
    required this.controller,
    required this.label,
    required this.icon,
    required this.onLocationSelected,
  });

  @override
  State<LocationInput> createState() => _LocationInputState();
}

class _LocationInputState extends State<LocationInput> {
  final RideService _rideService = RideService();
  List<PlaceSearchResult> _searchResults = [];
  bool _isSearching = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(12),
          ),
          child: TextField(
            controller: widget.controller,
            decoration: InputDecoration(
              hintText: widget.label,
              prefixIcon: Icon(widget.icon, color: Colors.grey[600]),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.all(16),
            ),
            onChanged: _onSearchChanged,
          ),
        ),

        // Search results
        if (_searchResults.isNotEmpty)
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: Colors.grey[300]!),
              borderRadius: BorderRadius.circular(8),
              boxShadow: const [
                BoxShadow(
                  color: Colors.black12,
                  blurRadius: 4,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: _searchResults.length,
              itemBuilder: (context, index) {
                final result = _searchResults[index];
                return ListTile(
                  leading: const Icon(Icons.location_on, color: Colors.grey),
                  title: Text(result.name),
                  subtitle: Text(result.address),
                  onTap: () {
                    widget.onLocationSelected(result.locationData);
                    setState(() {
                      _searchResults.clear();
                    });
                  },
                );
              },
            ),
          ),
      ],
    );
  }

  void _onSearchChanged(String query) async {
    if (query.length < 3) {
      setState(() {
        _searchResults.clear();
      });
      return;
    }

    setState(() {
      _isSearching = true;
    });

    try {
      final results = await _rideService.searchPlaces(query);
      setState(() {
        _searchResults = results;
        _isSearching = false;
      });
    } catch (e) {
      setState(() {
        _isSearching = false;
      });
    }
  }
}
