# Hotel Management System

## Overview

This is a comprehensive hotel management system built with Streamlit that provides a complete solution for managing hotel operations. The system includes user authentication, room management, financial tracking, and comprehensive reporting capabilities. It's designed as a multi-page web application with role-based access control and persistent data storage using JSON files.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web framework
- **Multi-page Application**: Organized using Streamlit's pages structure with separate modules for different functionalities
- **UI Components**: Custom CSS styling with responsive design and professional theming
- **Authentication Flow**: Session-based authentication with role-based access control

### Backend Architecture
- **Data Storage**: **PostgreSQL database** for permanent data persistence (migrated from JSON files)
- **Database Manager**: Comprehensive database-only data manager (`utils/database_data_manager.py`)
- **Authentication System**: Custom authentication module with password hashing (SHA-256)
- **Data Management**: Centralized database operations for all CRUD functions
- **Modular Design**: Utilities separated into reusable modules in the `utils/` directory

### Key Design Decisions
- **JSON over Database**: Chose JSON files for simplicity and ease of deployment without external dependencies
- **Role-based Access**: Implemented Admin/Manager/User roles with different permission levels
- **Session Management**: Streamlit's built-in session state for maintaining user sessions
- **Modular Structure**: Separated concerns with dedicated modules for auth, data management, and UI components

## Key Components

### Core Modules
1. **Authentication System** (`utils/auth.py`)
   - User credential management
   - Password hashing and verification
   - Session state management
   - Role-based access control

2. **Data Manager** (`utils/data_manager.py`)
   - JSON file operations
   - Data initialization and validation
   - CRUD operations for all entities
   - Date and ID generation utilities

3. **Main Application** (`app.py`)
   - Entry point and authentication gateway
   - Global configuration and styling
   - Session management

### Application Pages
1. **User Management** - Admin-only user creation and management
2. **Room Management** - Room status, check-in/check-out, maintenance tracking
3. **Sales Management** - Revenue tracking with cash/account categorization
4. **Expenditure Management** - Expense tracking and categorization
5. **Room Service** - Service requests and billing
6. **Complementary Rooms** - Free room allocation tracking
7. **Advance Payments** - Payment processing and tracking
8. **Dashboard** - Comprehensive analytics and reporting

### Data Entities
- **Users**: Authentication and role management
- **Rooms**: 8 rooms (101-108) with status tracking
- **Sales**: Revenue transactions with payment types
- **Expenditures**: Expense tracking with categories
- **Room Services**: Service requests and billing
- **Complementary Rooms**: Free accommodation tracking
- **Advance Payments**: Pre-payment management

## Data Flow

### Authentication Flow
1. User accesses application → Authentication check
2. If not authenticated → Login page display
3. Credential verification against JSON user store
4. Session state establishment with user role
5. Role-based page access control

### Data Management Flow
1. User interaction → Form submission
2. Data validation and processing
3. JSON file read/write operations
4. UI state refresh and feedback
5. Real-time metric calculations

### Business Logic Flow
- Room bookings update room status and generate sales records
- Service requests create billing entries
- Expenditures are categorized and tracked against budget
- Advance payments are applied to future bookings
- Dashboard aggregates all data for reporting

## External Dependencies

### Python Packages
- **streamlit**: Web framework for the entire application
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive charts and visualizations
- **auth**: Authentication utilities (note: this may need to be replaced with custom auth)

### System Dependencies
- **Python 3.11+**: Runtime environment
- **JSON**: Data persistence format
- **File System**: Local storage for data files

### Deployment Dependencies
- **Replit**: Hosting platform configuration
- **Nix**: Package management and environment setup
- **Autoscale**: Deployment target for scalability

## Deployment Strategy

### Current Setup
- **Platform**: Replit with Nix package management
- **Runtime**: Python 3.11 with streamlit server
- **Port**: 5000 with autoscale deployment target
- **Configuration**: Streamlit server configured for headless operation

### Data Persistence
- JSON files stored in `data/` directory
- Automatic initialization of required data structures
- File-based storage suitable for small to medium scale operations

### Scalability Considerations
- Current JSON-based storage is suitable for small hotels (up to 50 rooms)
- For larger operations, migration to PostgreSQL would be recommended
- Session state management supports concurrent users
- Stateless design allows for horizontal scaling

## Changelog

```
Changelog:
- June 23, 2025. Initial setup
- June 23, 2025. Added Outstanding Dues management with automatic sales integration
- June 23, 2025. Added Bill Upload system for admin review
- June 23, 2025. Simplified UI styling for better user experience
- June 23, 2025. Enhanced advance payment utilization with sales integration
- June 23, 2025. Added separate Cash Sales and Account Sales sections
- June 23, 2025. Outstanding dues and advance payments now automatically move to total sales when marked as paid/utilized
- June 23, 2025. Fixed advance payments to handle any advance amount vs actual total amount (e.g., ₹100 advance for ₹1000 total)
- June 23, 2025. Room service payments now properly categorize to Cash Sales or Account Sales sections
- June 23, 2025. Enhanced room management with proper booking system showing reserved/vacant status
- June 23, 2025. Added detailed room booking information visible to admin with full guest details
- June 23, 2025. Enhanced sales management with outstanding dues and advance payments integration
- June 23, 2025. Fixed room management functionality with proper booking system
- June 23, 2025. Updated admin dashboard with comprehensive metrics and alerts
- June 27, 2025. Added advance payment dates across all sections of the app for better tracking
- June 27, 2025. Enhanced date tracking system - payments maintain original advance/due dates and show in respective sales sections
- June 27, 2025. Fixed Financial Summary to show full advance amounts on original advance dates when completed
- June 27, 2025. Updated charts and trends to use advance dates for proper financial reporting
- June 27, 2025. Added multi-hotel support with separate admin accounts for Hotel 1 and Hotel 2
- June 27, 2025. Enhanced advance payment completion tracking - shows actual completion date (when fully paid) instead of advance date in both advance payments section and financial dashboard
- June 27, 2025. Updated financial summary to properly track completion dates for fully paid advance payments
- June 27, 2025. Added calendar date picker for advance payment reception - users can now select the specific date when receiving payments
- July 01, 2025. Added permanent system user "SazB" for Saz Valley Bhaderwah with password "sazbhaderwah"
- July 01, 2025. Added permanent system user "SazK" for Saz Valley Kistwar with password "sazkishtwar"
- July 01, 2025. Enhanced user persistence system to prevent credential corruption and ensure system users always exist
- July 01, 2025. Added backup and restore system for data recovery
- July 01, 2025. Protected system users (admin, SazB) from accidental deletion
- July 01, 2025. Implemented comprehensive data persistence system to prevent data loss
- July 01, 2025. Added automatic backup system with atomic save operations
- July 01, 2025. Created data integrity checker and auto-repair functionality
- July 01, 2025. Enhanced hotel-specific data file initialization and validation
- July 01, 2025. Created comprehensive Data Recovery page for admins to restore lost data
- July 01, 2025. Fixed critical error in Sales Management page preventing proper data display
- July 01, 2025. **MAJOR UPGRADE**: Migrated from Replit Agent to standard Replit environment with PostgreSQL database
- July 01, 2025. Added permanent PostgreSQL database storage to prevent data loss
- July 01, 2025. Created comprehensive Historical Data Entry page for entering past records with custom dates
- July 01, 2025. Implemented data integration system ensuring historical entries flow to respective sections and dashboards
- July 01, 2025. Enhanced advance payment and outstanding dues tracking with proper completion date handling
- July 01, 2025. All historical entries now automatically appear in their respective dashboards with correct dates
- July 01, 2025. **MAJOR ENHANCEMENT**: Added custom date selection to all primary data entry pages
- July 01, 2025. Restaurant, Sales Management, Expenditure Management, and Advance Payment pages now support historical date entry
- July 01, 2025. Users can now select any date when adding entries, enabling proper historical data entry across all sections
- July 01, 2025. Historical entries will appear in Financial Summary and Dashboard with correct dates for accurate reporting
- July 02, 2025. **CRITICAL UPGRADE**: Completely migrated entire system from JSON files to permanent PostgreSQL database
- July 02, 2025. Fixed all database schema issues and data type conflicts for proper data storage
- July 02, 2025. All data (sales, restaurant, expenditures, advance payments) now permanently stored in PostgreSQL
- July 02, 2025. Added comprehensive database-only data manager replacing all JSON file operations
- July 02, 2025. System now provides true data permanence - no more data loss from temporary storage
- July 02, 2025. **COMPLETE DATABASE MIGRATION**: Updated ALL pages to use PostgreSQL database
- July 02, 2025. All 20+ pages now connected to permanent database: Sales, Restaurant, Expenditures, Advance Payments, Room Service, Dashboard, Financial Summary, Data Download, etc.
- July 02, 2025. **CRITICAL FIX**: Resolved data mixing issue between hotels - disabled automatic migration to prevent data contamination
- July 02, 2025. **HOTEL DATA SEPARATION**: Saz Valley Bhaderwah (hotel2) and Saz Valley Kishtwar (hotel1) now maintain completely separate data
- July 02, 2025. Cleared mixed database records and implemented proper hotel data isolation
- July 02, 2025. **COMPLETE JSON ELIMINATION**: Removed ALL JSON file dependencies from every page and utility module
- July 02, 2025. Updated all remaining files (app.py, data_integration.py, data_monitor.py) to use database_data_manager exclusively
- July 02, 2025. Fixed all data structure conversion errors - database lists properly converted to dictionary format where needed
- July 02, 2025. Zero data loss guarantee - all new entries automatically saved to permanent PostgreSQL database with proper hotel separation
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
UI Style: Simple and clean design, not complex
Features: Outstanding dues with automatic sales integration, bill upload system, admin full control
```

## Technical Notes

### Authentication System
The system includes a custom authentication module with multi-hotel support. Users can be assigned to Hotel 1, Hotel 2, or Both Hotels. Each hotel can have its own admin while managers can oversee both properties.

### Database Migration Path
While the system currently uses JSON files, it's designed with abstraction layers that would allow easy migration to PostgreSQL using Drizzle ORM in the future. The data manager module can be extended to support database operations without changing the application logic.

### Security Considerations
- Passwords are hashed using SHA-256
- Session-based authentication prevents unauthorized access
- Role-based access control limits functionality based on user privileges
- File-based storage requires appropriate file system permissions

### Performance Optimization
- Data is loaded on-demand for each page
- JSON files are kept small and focused
- Streamlit caching can be implemented for frequently accessed data
- Real-time calculations are optimized for the expected data volumes