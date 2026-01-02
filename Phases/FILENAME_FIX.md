# Filename Fix for MSI Download

## Issue
The downloaded MSI file had a corrupted filename: `PrismTrack_Agent_S18NZD4.msi_` (with trailing underscore)

## Root Cause
The filename extraction from the `Content-Disposition` header was not properly handling edge cases, and the backend header format could be improved for better browser compatibility.

## Fixes Applied

### Backend (`backend/api/v1/endpoints/tenant.py`)
1. **Improved Content-Disposition Header**:
   - Added RFC 5987 format (`filename*=UTF-8''encoded_filename`) for better browser compatibility
   - Kept standard format (`filename="value"`) as fallback
   - Properly URL-encoded the filename for RFC 5987 format

2. **Filename Sanitization**:
   - Ensured filename is stripped of any trailing whitespace
   - Clean filename format: `PrismTrack_Agent_{org_id}.msi`

### Frontend (`frontend/js/api.js`)
1. **Improved Filename Extraction**:
   - First tries to extract from RFC 5987 format (`filename*=UTF-8''...`)
   - Falls back to standard format (`filename="..."`)
   - Properly decodes URL-encoded filenames

2. **Filename Cleanup**:
   - Removes trailing underscores and spaces
   - Fixes `.msi_` to `.msi` (handles multiple underscores)
   - Ensures filename always ends with `.msi`
   - Multiple cleanup passes to handle edge cases

## Testing
- Backend sends: `attachment; filename="PrismTrack_Agent_S18NZD4.msi"; filename*=UTF-8''PrismTrack_Agent_S18NZD4.msi`
- Frontend extracts and cleans: `PrismTrack_Agent_S18NZD4.msi`
- Download uses clean filename: `PrismTrack_Agent_S18NZD4.msi`

## Result
✅ Filename is now correctly formatted without trailing underscores
✅ Works across different browsers
✅ Handles edge cases in header parsing

