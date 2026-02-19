# Automated Test Suite

This directory contains the comprehensive automated testing system for the Multi-University AI Chatbot Platform.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

### Run All Tests

```bash
# From project root
pytest tests/ -v
```

or

```bash
python run_tests.py
```

### Run Specific Test Suite

```bash
python run_tests.py auth        # Authentication tests
python run_tests.py roles       # Role and permission tests
python run_tests.py chatbot     # Chatbot pipeline tests
python run_tests.py knowledge   # Knowledge base tests
python run_tests.py faq         # FAQ system tests
python run_tests.py context     # Context memory tests
python run_tests.py analytics   # AI analytics tests
python run_tests.py isolation   # University isolation tests
python run_tests.py database    # Database integrity tests
```

## Test Files

- `conftest.py` - Test configuration and fixtures
- `test_authentication.py` - Authentication and user management
- `test_roles_permissions.py` - Role-based access control
- `test_chatbot_pipeline.py` - Complete chatbot message flow
- `test_knowledge_base.py` - Knowledge base CRUD and search
- `test_faq_system.py` - FAQ retrieval and filtering
- `test_context_memory.py` - Conversation context management
- `test_ai_analytics.py` - Analytics tracking and aggregation
- `test_university_isolation.py` - Multi-tenant data isolation
- `test_database_integrity.py` - Database models and relationships

## Test Coverage

**145+ automated tests** covering:

✓ User authentication and authorization
✓ Role-based access control
✓ Chatbot message pipeline
✓ Knowledge base operations
✓ FAQ system
✓ Conversation context memory
✓ AI analytics tracking
✓ University data isolation
✓ Database integrity

## Key Features

- **Isolated Test Environment**: Each test runs with its own clean database
- **Comprehensive Fixtures**: Pre-populated test data for all scenarios
- **Mocked External Services**: AI calls are mocked for fast, reliable tests
- **Security Testing**: Verifies access controls and data isolation
- **Performance Testing**: Checks query efficiency
- **Full Coverage**: Tests all critical user flows

## Test Data

Fixtures provide:

- 3 Universities (Batna 2, Algiers 1, Constantine 1)
- 3 Departments across universities
- 7 Users (super admin, university admins, students)
- 6 Knowledge base entries
- 5 Chat sessions with message history

## Documentation

For complete documentation, see [TESTING.md](../TESTING.md) in the project root.

## Writing Tests

Example test structure:

```python
def test_feature_name(self, authenticated_client, sample_data, db_session):
    """Test description."""
    # Arrange
    test_input = {...}
    
    # Act
    response = authenticated_client.post('/endpoint', json=test_input)
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data['key'] == expected_value
```

## Best Practices

1. Use descriptive test names
2. Leverage existing fixtures
3. Test one behavior per test
4. Mock external API calls
5. Use clear assertions
6. Keep tests independent

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```bash
pytest tests/ -v --tb=short --disable-warnings
```

## Troubleshooting

### Import Errors
Run tests from the project root directory.

### Database Errors
Tests use temporary SQLite databases. If errors occur, check test configuration.

### Test Failures
- Read error messages carefully
- Check fixture setup
- Verify mock configurations

## Support

For questions or issues, please contact the development team or refer to the main TESTING.md documentation.
