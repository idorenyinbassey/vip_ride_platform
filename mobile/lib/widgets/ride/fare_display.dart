import 'package:flutter/material.dart';
import '../../models/ride_models.dart';

class FareDisplay extends StatelessWidget {
  final FareEstimate fareEstimate;
  final bool isLoading;

  const FareDisplay({
    super.key,
    required this.fareEstimate,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Row(
          children: [
            SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            SizedBox(width: 12),
            Text('Calculating fare...'),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green[200]!),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Estimated Fare',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              Text(
                '${fareEstimate.currency} ${fareEstimate.totalFare.toStringAsFixed(0)}',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green[700],
                ),
              ),
            ],
          ),

          if (fareEstimate.surgeMultiplier > 1.0) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.orange[100],
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.trending_up, size: 16, color: Colors.orange[700]),
                  const SizedBox(width: 4),
                  Text(
                    '${fareEstimate.surgeMultiplier.toStringAsFixed(1)}x surge pricing',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.orange[700],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Breakdown
          const SizedBox(height: 8),
          _buildFareBreakdown(),
        ],
      ),
    );
  }

  Widget _buildFareBreakdown() {
    return Column(
      children: [
        _buildFareRow('Base Fare', fareEstimate.baseFare),
        _buildFareRow('Distance', fareEstimate.distanceFare),
        if (fareEstimate.timeFare > 0)
          _buildFareRow('Time', fareEstimate.timeFare),
        if (fareEstimate.surgeMultiplier > 1.0)
          _buildFareRow(
            'Surge',
            (fareEstimate.totalFare -
                (fareEstimate.baseFare +
                    fareEstimate.distanceFare +
                    fareEstimate.timeFare)),
          ),
        const Divider(height: 16),
        _buildFareRow('Total', fareEstimate.totalFare, isTotal: true),
      ],
    );
  }

  Widget _buildFareRow(String label, double amount, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: isTotal ? 14 : 12,
              fontWeight: isTotal ? FontWeight.w600 : FontWeight.normal,
              color: isTotal ? Colors.black : Colors.grey[600],
            ),
          ),
          Text(
            '${fareEstimate.currency} ${amount.toStringAsFixed(0)}',
            style: TextStyle(
              fontSize: isTotal ? 14 : 12,
              fontWeight: isTotal ? FontWeight.w600 : FontWeight.normal,
              color: isTotal ? Colors.black : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}
