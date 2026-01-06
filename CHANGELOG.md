# Changelog

All notable changes to the CalcsLive Plug for Inventor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Multi-domain support for CalcsLive platform (calcslive.com + calcs.live)
- Enhanced CORS configuration for both primary and legacy domains

### Changed
- Updated all documentation links to use www.calcslive.com as primary domain
- Corrected API endpoint documentation (/inventor/health instead of /inventor/status)
- Updated dashboard URLs throughout documentation
- Updated Brave browser troubleshooting instructions for new domain

### Fixed
- CORS configuration now allows requests from both calcslive.com and calcs.live domains
- Documentation consistency across README and code comments

## [1.0.0] - 2025-11-16

### Added
- **ArticleId Management**: Create ArticleId parameter programmatically via `/inventor/parameters/create` endpoint
- **Mapping Deletion**: Delete parameter mappings via `/inventor/parameters/mapping` DELETE endpoint
- **Comprehensive Testing**: 23 unit tests covering comment parsing, mapping, and edge cases
- **Production Ready Status**: Fully tested and documented for production use

### Changed
- Enhanced error handling and validation across all endpoints
- Improved documentation with clearer examples and use cases
- Optimized performance for parameter synchronization

### Fixed
- Comment field parsing edge cases
- Parameter mapping persistence issues
- Error messages now more descriptive and actionable

## [0.9.0] - 2025-11-14

### Added
- **Comment-Based Mapping Architecture**: Non-intrusive mapping using User Parameter Comment field
- **Bidirectional Sync**: CalcsLive ⟷ Inventor parameter synchronization
- **Engineering-Driven Modeling (EDM)**: Full workflow support for iterative design refinement
- **RESTful API**: FastAPI-based bridge server with comprehensive endpoints
- **Auto-Generated Documentation**: Swagger UI and ReDoc available at `/docs` and `/redoc`

### Endpoints
- `GET /` - Health check endpoint
- `GET /inventor/health` - Inventor-specific health check
- `GET /inventor/document` - Get active document information
- `GET /inventor/parameters` - Retrieve all User Parameters with mapping info
- `POST /inventor/parameters/mapping` - Create/update parameter mappings
- `DELETE /inventor/parameters/mapping` - Remove parameter mappings
- `POST /inventor/parameters/create` - Create new User Parameters

### Documentation
- Complete README with quick start guide
- Architecture documentation
- Troubleshooting section
- Comment syntax specification
- Example workflows

### Technical Features
- **Unit Categories**: 67+ engineering disciplines (mechanical, thermal, electrical, fluid, civil)
- **Comment Syntax**: `CA0:symbol #note` format for mapping
- **Dimensional Analysis**: Automatic dimensional tracking and validation
- **CORS Support**: Pre-configured for production use with CalcsLive dashboard
- **Error Handling**: Comprehensive error messages and fallback behavior

### Browser Support
- Chrome, Edge, Firefox (full support)
- Brave (requires Shield disable for localhost connections)

## [0.1.0] - 2025-11-01 (Initial Release)

### Added
- Basic bridge server implementation
- Initial COM API wrapper for Inventor
- Core parameter reading functionality
- Proof of concept for CalcsLive integration

---

## Version History Summary

- **v1.0.0** (2025-11-16): Production ready release with ArticleId management
- **v0.9.0** (2025-11-14): Feature complete with full EDM workflow
- **v0.1.0** (2025-11-01): Initial proof of concept

---

## Migration Guides

### Migrating to Multi-Domain Support (Unreleased → 1.0.0)

**No breaking changes!** Both `calcs.live` and `calcslive.com` are fully supported.

**Recommended Actions**:
1. Update bookmarks to use `www.calcslive.com/inventor/dashboard`
2. If using Brave browser, update Shield exceptions for new domain
3. No code changes required - CORS already configured for both domains

**For Developers**:
- CORS configuration in `main.py` now includes both domains
- Documentation uses `www.calcslive.com` as primary reference
- Legacy `calcs.live` URLs continue to work indefinitely

---

## Community & Support

- **Issues**: [GitHub Issues](https://github.com/CalcsLive/calcslive-plug-4-inventor/issues)
- **Documentation**: [calcslive.com/help/inventor-integration](https://www.calcslive.com/help/inventor-integration)
- **Dashboard**: [calcslive.com/inventor/dashboard](https://www.calcslive.com/inventor/dashboard)
- **Email**: don.wen@calcs.live

---

**Last Updated**: January 6, 2026
**Current Version**: 1.0.0 (with multi-domain support)
