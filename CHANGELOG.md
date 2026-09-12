# Changelog

All notable changes to the CalcsLive Plug for Inventor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `POST /inventor/document/update` endpoint — triggers `doc.Update()` + `ActiveView.Update()` via COM so the dashboard can auto-refresh the 3D model after pushing parameter changes
- Root endpoint `GET /` now returns an `endpoints` array listing all available routes with method, path, and description

### Changed
- CLAUDE.md: documented `POST /inventor/document/update`, added "Starting the Bridge" section with `C:\E3d\auto-scripts\inventor-bridge.bat` global launcher pattern
- README.md: added `POST /inventor/document/update` to API Endpoints section and Project Status checklist

## [1.3.0] - 2026-07-22

### Added
- **HTTPS Bridge**: Bridge now requires HTTPS — start with `uvicorn` + `--ssl-certfile` / `--ssl-keyfile` flags using mkcert locally-trusted certificate
- **Private Network Access (PNA) middleware**: Raw ASGI middleware responds correctly to Chrome's PNA preflight (`Access-Control-Allow-Private-Network: true`)
- **mkcert setup instructions**: README quick start covers one-time certificate generation

### Fixed
- Chrome 121+ and Brave now connect to bridge without security errors (PNA policy compliance)

### Changed
- HTTPS required for Chrome/Brave — plain HTTP no longer supported
- README updated with Chrome/Brave "Apps on device" toggle instructions and Brave Shields workaround

## [1.2.0] - 2026-03-xx

### Added
- `POST /inventor/convert` endpoint — unit conversion via Inventor's `UnitsOfMeasure.ConvertUnits()` API
- `userValue` / `userUnit` fields in parameter export — preserves user-typed unit from expressions (e.g., "24 in" when display is "mm")

### Notes
- Temperature conversions (°C, °F, K) not supported by Inventor's API — use CalcsLive for thermodynamics

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

- **Unreleased**: `/inventor/document/update` endpoint, root endpoint listing
- **v1.3.0** (2026-07-22): HTTPS bridge, Chrome/Brave PNA compatibility
- **v1.2.0** (2026-03): Unit conversion endpoint, userUnit preservation
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

**Last Updated**: September 12, 2026
**Current Version**: 1.3.0 (unreleased changes pending next tag)
