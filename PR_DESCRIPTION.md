## PR Title: Fix connection retry issue and improve project packaging and performance

### Description
This PR addresses a critical issue where users were unable to retry connecting to a network after entering an incorrect password. Additionally, it includes several improvements to project structure, build process, documentation, and performance enhancements.

### Key Changes

#### 1. Bug Fix: Connection Retry Issue (fixes #4)
- **Problem**: When users entered incorrect passwords, nmcli would create connection profiles with invalid credentials. On subsequent attempts, nmcli would try to reuse these failed profiles instead of creating fresh connections, causing all following attempts to fail.
- **Solution**: 
  - Added a `_cleanup_failed_connection` helper method to delete failed connection profiles
  - Updated `connect_to_network` to call this cleanup method on connection failures
  - This ensures users can retry connecting after entering wrong passwords

#### 2. Performance Enhancements
- Implemented intelligent network scan caching with 2-second cache duration
- Reduced network scan sleep time from 0.5s to 0.1s for faster scanning
- Added cache invalidation when network connections are modified
- Optimized UI updates with batch processing and better widget management
- Improved threading model for background operations

#### 3. UI/UX Improvements
- Standardized UI elements with consistent heights (min-height: 30px) across all text/input boxes
- Added CSS classes for better styling consistency
- Improved password dialog with better styling and placeholder text
- Enhanced network list with better visual feedback during scanning
- Updated all UI components with consistent spacing and margins

#### 4. Build System Improvements
- Fixed Nuitka build script to properly include GTK dependencies
- Removed specific gi.repository module includes that caused build failures
- Added proper Cairo graphics support
- Successfully builds standalone executable at dist/nmgui.bin

#### 5. Project Structure Refactoring
- Reorganized project structure for professional packaging
- Standardized UI elements for better consistency
- Added proper packaging configuration files (pyproject.toml, setup.py)
- Created comprehensive README.md with usage instructions

#### 6. Documentation and Metadata Updates
- Updated version numbers across the project from 1.0.0 to 1.1.0
- Enhanced README with installation instructions for Arch Linux (AUR) and other distributions
- Added Hyprland window management configuration
- Updated author information
- Fixed missing newlines at end of files
- Updated release download URLs in documentation

### Testing
- Verified the connection retry fix resolves the reported issue
- Confirmed standalone executable builds and runs correctly with all functionality preserved
- Tested installation instructions on multiple distributions
- Performance improvements validated through manual testing

### Related Issues
- Fixes #4 (Connection retry issue)

This PR significantly improves the reliability, performance, and user experience of the application while making it easier to install and distribute.