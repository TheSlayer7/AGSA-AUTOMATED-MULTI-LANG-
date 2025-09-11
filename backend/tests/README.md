# Tests Directory

This directory contains all test files and utilities for the AGSA DigiLocker backend.

## Files

### Test Scripts
- **`simple_test.py`** - Basic API endpoint testing
- **`test_api.py`** - Comprehensive API testing with mock data
- **`test_dynamic_api.py`** - Advanced API testing with database integration

### Utilities
- **`populate_sample_data.py`** - Script to populate the database with sample data

## Usage

### Running Tests

From the backend directory, you can run the tests as follows:

```bash
# Run simple API test
uv run python tests/simple_test.py

# Run comprehensive API test
uv run python tests/test_api.py

# Run dynamic API test (requires database)
uv run python tests/test_dynamic_api.py

# Populate sample data
uv run python tests/populate_sample_data.py
```

### Prerequisites

1. **Django server must be running**:
   ```bash
   uv run python manage.py runserver
   ```

2. **Database must be migrated**:
   ```bash
   uv run python manage.py migrate
   ```

3. **For dynamic tests, sample data should be populated**:
   ```bash
   uv run python tests/populate_sample_data.py
   ```

## Test Structure

### Simple Test (`simple_test.py`)
- Tests basic API connectivity
- Checks endpoint availability
- Basic OTP request testing

### API Test (`test_api.py`)
- Full authentication flow testing
- Document listing and download
- Error handling verification

### Dynamic API Test (`test_dynamic_api.py`)
- Database-backed testing
- Real file upload/download testing
- Session management verification

### Sample Data (`populate_sample_data.py`)
- Creates 4 sample users
- Creates 10 document types
- Generates sessions and OTP requests
- Provides ready-to-use test data

## Notes

- All tests require the Django development server to be running
- Tests use the sample data created by `populate_sample_data.py`
- For file upload testing, use the Django admin interface at http://127.0.0.1:8000/admin/
