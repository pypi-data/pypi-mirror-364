# Changelog
## [1.0.6](https://github.com/matthttam/ThreeCXAPI/releases/tag/1.0.6) - 2025-07-24
[pypi package](https://pypi.org/project/threecxapi/1.0.6.post1/)

### Changed
- **Breaking:** Rewrite of pbx, enums, and response objects. Enums has moved under pbx.
### Added
- Support for 3CX openapi 3.0.4
- All additional Pbx and Enum objects
- Added the openapi yml files for future reference in .openapi folder.
- Added swagger generator files for future use.

### Removed
- Old pbx and enum objects that are no longer in the 3.0.4 standard

### Fixed
- Enums now allow arbitrary string values to prevent issues if 3CX changes their schema. Warnings are logged to the field object and parent object.

## [1.0.5](https://pypi.org/project/threecxapi/1.0.5.post1/) - 2025-01-29
_Stable Pypi release._
### Added
- Support for 3cx openapi 3.0.0

## [1.0.4](https://pypi.org/project/threecxapi/1.0.4.post1/) - 2025-01-28
_Initial Pypi release._
## [1.0.3](https://github.com/matthttam/ThreeCXAPI/releases/tag/1.0.3) - 2025-01-28
_Preparing for Pypi._

## [1.0.2](https://github.com/matthttam/ThreeCXAPI/releases/tag/1.0.2) - 2025-01-28
_Preparing for Pypi._

## [1.0.1](https://github.com/matthttam/ThreeCXAPI/releases/tag/1.0.1) - 2025-01-28
_Preparing for Pypi._

## [1.0.1](https://github.com/matthttam/ThreeCXAPI/releases/tag/1.0.0) - 2025-01-28

_Initial release._