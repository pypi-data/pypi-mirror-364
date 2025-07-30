## [1.0.0] - 2024-07-28

### Added
- **Base Response**: Introduced a foundational response class for consistent API response handling.
- **ID Generation**: Implemented a utility for generating unique identifiers across the application.
- **Paginator**: Added a pagination utility to streamline data retrieval and presentation.
- **Request Utils**: Included helper functions to facilitate and standardize API request handling.
- **API Exception Middleware**: Integrated middleware to centralize and manage API exception handling.

### Changed
- **API Exceptions**: Enhanced the API exception system with the addition of the `ApiResponse` class for more structured error responses.

## [1.0.1] - 2024-07-28

### Added
- **Added Third Pary API Response**: Introduced a new class ThirdPartyApiResponse to handle and process responses from third-party APIs.
- **Added Class Utility**: Introduced a ClassUtility class and added a function which converts an object to dictionary.


## [1.0.2] - 2025-05-16
### Added
- **APM Alerts Command**: Introduced an APM alerts command to give alerts to discord channel in case of any internal server errors.

## [1.0.3] - 2025-05-16
### Added
- **SkillspeApiException**: Introduced custom data field in SkillspeApiException.