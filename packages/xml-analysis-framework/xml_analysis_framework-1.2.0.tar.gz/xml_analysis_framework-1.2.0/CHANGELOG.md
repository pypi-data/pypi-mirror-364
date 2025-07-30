# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-01-25

### Changed
- **Repository Information**: Updated all GitHub links to point to official Red Hat AI Americas repository
  - Changed from: `https://github.com/wjackson/xml-analysis-framework`
  - Changed to: `https://github.com/redhat-ai-americas/xml-analysis-framework`
  - Updated in setup.py, pyproject.toml, README.md, and CONTRIBUTING.md
- **Contact Information**: Updated author email to `wjackson@redhat.com`

### Fixed
- **Smart Chunking Example**: Updated README.md smart chunking example to include required analysis format conversion

## [1.1.0] - 2025-01-25

### Fixed
- **Package Description**: Clarified that this is a preprocessing framework, not one that performs AI/ML operations
  - Changed from: "Comprehensive framework for analyzing XML documents with AI/ML processing support" 
  - Changed to: "XML document analysis and preprocessing framework designed for AI/ML data pipelines"
  - Updated in setup.py, pyproject.toml, README.md, and src/__init__.py
- **Documentation Updates**: Updated all import examples in README.md to reflect correct package structure
  - Changed `from xml_analysis_framework import ...` to `from core.* import ...`
  - Changed `from src.core.* import ...` to `from core.* import ...`
  - Updated API method signatures and return value access patterns
  - Fixed chunking workflow examples to use `ChunkingOrchestrator` correctly

### Changed
- **Import Structure**: All documentation now correctly shows the installed package import structure:
  - Basic analysis: `from core.schema_analyzer import XMLSchemaAnalyzer`
  - Enhanced analysis: `from core.analyzer import XMLDocumentAnalyzer`
  - Chunking: `from core.chunking import ChunkingOrchestrator, XMLChunkingStrategy`

### Added
- **API Examples**: Added correct examples showing:
  - Proper access to `DocumentTypeInfo` attributes (`.type_name`, `.confidence`)
  - Correct `SpecializedAnalysis` attribute access (`.ai_use_cases`, `.structured_data`)
  - Format conversion for chunking analysis
  - Token estimation using `XMLChunkingStrategy().estimate_tokens()`

### Updated
- **Version**: Bumped to 1.1.0 in setup.py and src/__init__.py
- **Examples**: Updated examples/basic_analysis.py and examples/enhanced_analysis.py imports
- **Documentation**: All README.md code examples now work correctly with the installed package

### Validated
- All documentation examples tested and verified to work with the actual installed package structure
- Confirmed compatibility with existing PyPI package (1.0.0) → updated for new release (1.1.0)

## [1.0.0] - 2025-01-25

### Added
- Initial release with XML analysis framework
- 29 specialized XML handlers
- Chunking strategies for AI/ML processing
- Core analysis engine with schema detection