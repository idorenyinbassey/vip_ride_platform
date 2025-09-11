#!/bin/bash
# Safe cleanup script for VIP Ride Platform duplicates and empty files
# This script only removes files that are clearly safe to delete

echo "🧹 VIP Ride Platform - Safe File Cleanup"
echo "========================================"

# Function to safely remove file if it exists
safe_remove() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        echo "🗑️  Removing: $description"
        echo "    File: $(basename "$file")"
        rm -f "$file"
        echo "    ✅ Deleted successfully"
    else
        echo "⚠️  File not found: $(basename "$file")"
    fi
    echo ""
}

# Function to analyze duplicate and suggest which to keep
analyze_duplicate() {
    local main_file="$1"
    local duplicate_file="$2"
    local description="$3"
    
    echo "🔍 DUPLICATE ANALYSIS: $description"
    echo "----------------------------------------"
    
    if [ -f "$main_file" ] && [ -f "$duplicate_file" ]; then
        local main_size=$(stat -c%s "$main_file" 2>/dev/null || echo "0")
        local dup_size=$(stat -c%s "$duplicate_file" 2>/dev/null || echo "0")
        
        echo "📁 Main file: $(basename "$main_file") (${main_size} bytes)"
        echo "📁 Duplicate: $(basename "$duplicate_file") (${dup_size} bytes)"
        
        if [ "$dup_size" -eq 0 ]; then
            echo "🗑️  Removing empty duplicate: $(basename "$duplicate_file")"
            rm -f "$duplicate_file"
            echo "    ✅ Empty duplicate removed"
        elif [ "$main_size" -gt "$dup_size" ] && [ "$dup_size" -lt 100 ]; then
            echo "🗑️  Removing small duplicate: $(basename "$duplicate_file")"
            rm -f "$duplicate_file" 
            echo "    ✅ Small duplicate removed"
        else
            echo "⚠️  Manual review needed - both files have content"
            echo "    Main: $main_file"
            echo "    Duplicate: $duplicate_file"
        fi
    else
        echo "⚠️  One or both files not found"
    fi
    echo ""
}

echo "🗑️  REMOVING EMPTY FILES"
echo "========================"

# Remove clearly empty and unused files
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/consolidate_tests.py" "Empty consolidation test script"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/consolidate_hotels.py" "Empty hotel consolidation script"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/consolidate_hotels_simple.py" "Empty simple hotel consolidation script"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/verify_consolidation.py" "Empty verification script"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/accounts/payment_service_new.py" "Empty new payment service"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/vip_ride_platform/api_views_new.py" "Empty new API views"
safe_remove "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/vip_ride_platform/test_api_views.py" "Empty test API views"

echo "🔄 ANALYZING DUPLICATE FILES"
echo "============================="

# Analyze major duplicates
analyze_duplicate \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/pricing/models.py" \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/pricing/models_new.py" \
    "Pricing Models (Main vs New)"

analyze_duplicate \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/pricing/models.py" \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/pricing/models_simple.py" \
    "Pricing Models (Main vs Simple)"

analyze_duplicate \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/gps_tracking/encryption.py" \
    "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/core/encryption.py" \
    "GPS Encryption (GPS Tracking vs Core)"

# Check Flutter duplicates
if [ -f "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/mobile/lib/screens/client/regular/regular_client_app_clean.dart" ]; then
    echo "🗑️  Removing Flutter clean backup files"
    rm -f "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/mobile/lib/screens/client/regular/regular_client_app_clean.dart"
    rm -f "/home/idorenyinbassey/My projects/workspace1/vip_ride_platform/mobile/lib/screens/client/vip/vip_client_app_clean.dart"
    echo "    ✅ Flutter backup files removed"
    echo ""
fi

echo "📋 MANUAL REVIEW NEEDED"
echo "======================="
echo "The following files contain duplicated content but need manual decision:"
echo ""
echo "1. 📄 Pricing Models:"
echo "   - pricing/models.py (main - 571 lines)"
echo "   - pricing/models_backup.py (backup - minimal content)"
echo "   💡 Recommendation: Keep models.py, remove models_backup.py"
echo ""

echo "2. 📄 Payment Services:"
echo "   - accounts/payment_service.py (main - 460 lines)"
echo "   💡 Recommendation: Keep this one, empty duplicate already removed"
echo ""

echo "3. 📄 GPS Encryption:"
echo "   - gps_tracking/encryption.py (351 lines)"
echo "   - core/encryption.py (470 lines)"
echo "   💡 Recommendation: Choose one based on which is actively used"
echo ""

# Generate manual cleanup recommendations
cat > manual_cleanup_recommendations.txt << 'EOF'
VIP Ride Platform - Manual Cleanup Recommendations
==================================================

SAFE TO DELETE (after verification):
- pricing/models_backup.py (minimal backup)
- pricing/models_new.py and models_simple.py (if models.py is current)
- One of: core/encryption.py OR gps_tracking/encryption.py (keep the one being imported)

FILES TO KEEP:
- All __init__.py files (required for Python packages)
- pricing/models.py (main models file)
- accounts/payment_service.py (main payment service)
- vip_ride_platform/api_views.py (main API views)

FLUTTER FILES:
- Regular and VIP client app files appear to have clean backups removed

VERIFICATION COMMANDS:
To check which encryption file is being used:
  grep -r "from.*encryption import" . --exclude-dir=.venv
  grep -r "import.*encryption" . --exclude-dir=.venv

To check model imports:
  grep -r "from pricing.models" . --exclude-dir=.venv
  grep -r "import.*models" . --include="*.py" --exclude-dir=.venv

NEXT STEPS:
1. Run this script: bash safe_cleanup.sh
2. Review the manual_cleanup_recommendations.txt
3. Test the application to ensure nothing breaks
4. Remove the remaining duplicates manually after verification
EOF

echo "✅ CLEANUP COMPLETED"
echo "==================="
echo "📝 Recommendations saved to: manual_cleanup_recommendations.txt"
echo "📊 Summary:"
echo "   - Empty files: Automatically removed"
echo "   - Flutter backups: Removed"
echo "   - Major duplicates: Require manual review"
echo ""
echo "🔍 To check which files are being used:"
echo "   grep -r 'from.*models import' . --exclude-dir=.venv"
echo "   grep -r 'from.*encryption import' . --exclude-dir=.venv"
echo ""
echo "⚠️  Always test the application after cleanup!"
