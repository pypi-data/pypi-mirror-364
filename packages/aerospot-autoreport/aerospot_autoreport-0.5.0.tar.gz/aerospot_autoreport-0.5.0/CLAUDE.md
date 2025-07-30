# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoReportV3 is an enterprise-grade automated report generation system for water quality monitoring using UAV aerial data. The project uses a modular architecture with domain-driven design, supporting pluggable business domains.

**Core Features:**
- UAV data processing and analysis
- Water quality modeling and prediction
- Satellite map visualization generation
- Professional Word document report generation
- Multi-format data support (CSV, KML, ZIP)

## Development Environment

**Required Tools:**
- Python 3.10+ (Python 3.11 recommended)
- uv for dependency management
- pytest for testing

**Environment Setup:**
```bash
# Run main application
uv run python interface.py [config.json]

# Run with default config
uv run python interface.py  # uses test.json by default

# Run tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/end_to_end/

# Generate test coverage report
uv run pytest --cov=src/autoreport tests/
```

## Architecture Overview

The system follows a **layered architecture** with **pluggable domain modules**:

### Core Data Flow
```
Config Loading → Resource Download → Data Extraction → Data Processing → 
Model Training → Visualization → Report Generation
```

### Key Components

**Core Modules (`src/autoreport/core/`):**
- `generator.py`: Report generation engine
- `resource_manager.py`: Resource download and caching
- `error_handler.py`: Unified error handling
- `config_validator.py`: Configuration validation

**Domain System (`src/autoreport/domains/`):**
- Pluggable architecture for different monitoring domains
- `water_quality/`: Water quality monitoring implementation
- Base interfaces for domain extension

**Data Processing (`src/autoreport/processor/`):**
- `data/`: Core data processing pipeline
- `maps.py`: Satellite map generation and visualization
- `extractor.py`: ZIP file extraction
- `downloader.py`: Resource downloading

**Document Generation (`src/autoreport/document/`):**
- `pages.py`: Page layout and formatting
- `paragraphs.py`: Text content generation
- `tables.py`: Table generation
- `images.py`: Image processing and embedding

## Configuration System

**Configuration File Structure:**
```json
{
  "domain": "water_quality",
  "data_root": "./AutoReportResults/",
  "company_info": {
    "name": "Company Name",
    "logo_path": "OSS_URL",
    "satellite_img": "OSS_URL",
    "wayline_img": "OSS_URL",
    "file_url": "OSS_URL",
    "measure_data": "OSS_URL",
    "kml_boundary_url": "OSS_URL_OPTIONAL"
  },
  "domain_config": {
    "enabled_indicators": ["nh3n", "tp", "cod"],
    "quality_standards": "GB_3838_2002"
  }
}
```

**Key Configuration Points:**
- `domain`: Determines which domain processor to use
- `data_root`: Base output directory for all generated files
- `company_info`: Resource URLs and company details
- `kml_boundary_url`: Optional KML file URL for custom boundary definition
- `domain_config`: Domain-specific processing parameters

**KML Boundary Feature:**
- If `kml_boundary_url` is provided and valid, the system will use KML-defined boundaries for map generation
- If no KML file is provided or the file is invalid, the system falls back to automatic alpha_shape boundary detection
- KML boundaries are used for interpolation heat maps, clean transparent maps, and level distribution maps
- Supports complex polygonal boundaries defined in standard KML format

## Development Workflow

**Main Entry Point:**
- `interface.py`: Main application entry with cache control
- `src/autoreport/main.py`: Core application logic

**Common Development Tasks:**
1. **Adding New Domain**: Implement domain interfaces in `src/autoreport/domains/`
2. **Data Processing**: Extend processors in `src/autoreport/processor/data/`
3. **Visualization**: Modify map generation in `src/autoreport/processor/maps.py`
4. **Report Templates**: Update document generators in `src/autoreport/document/`

**Testing Strategy:**
- Unit tests for individual components
- Integration tests for data processing workflows
- End-to-end tests for complete report generation

## Key Dependencies

**Core Dependencies:**
- `pandas`, `numpy`: Data processing
- `python-docx`, `spire-doc`: Document generation
- `matplotlib`, `seaborn`: Visualization
- `autowaterqualitymodeler`: Water quality modeling
- `scikit-learn`: Machine learning
- `opencv-python`: Image processing

**Platform-Specific:**
- `pywin32`: Windows-specific functionality (auto-installed on Windows)

## Cache and Resource Management

**Cache Control:**
- Modify `CACHE_ENABLED` in `interface.py` to enable/disable caching
- Resources cached for 15 minutes by default
- Cache location: `global_cache/` directory

**Resource Types:**
- Logo images
- Satellite imagery
- Wayline images
- Data files (ZIP format)
- Measurement data (CSV format)

## Branch-Specific Development

**Current Branch: main**
- Focus: Stable release branch with all features
- Latest Updates: Dev branch improvements integrated
- Status: Ready for v0.5.0 release

**Recent Updates:**
- ✅ KML边界支持功能已完整集成并合并
- ✅ 支持从配置文件获取KML边界文件
- ✅ 智能边界检测（kml/alpha_shape/convex_hull/density_based）
- ✅ 自动回退机制确保稳定性
- ✅ 完整测试覆盖和文档更新
- ✅ 添加设备兼容性信息（大疆机场2、大疆机场3）
- ✅ 优化项目结构和gitignore配置

**Available Features:**
- UAV数据处理和分析
- 水质建模和预测
- 卫星地图可视化生成
- 专业Word文档报告生成
- 多格式数据支持（CSV、KML、ZIP）
- 可选KML边界定义支持
- 设备兼容性增强

**Current State:**
- 主分支包含最新的稳定功能
- 所有代码已经过测试验证
- 准备发布v0.5.0版本

## Common Commands

```bash
# Run with specific configuration
uv run python interface.py path/to/config.json

# Run with cache disabled (modify CACHE_ENABLED in interface.py)
uv run python interface.py

# Run single test file
uv run pytest tests/unit/test_config_validator.py

# Run with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=src/autoreport --cov-report=html tests/
```

## Output Structure

Generated reports are organized in timestamped directories:
```
AutoReportResults/
└── report_YYYYMMDD_HHMMSS/
    ├── downloads/          # Downloaded resources
    ├── extracted/          # Extracted data files
    ├── maps/              # Generated visualizations
    ├── reports/           # Final Word documents
    ├── logs/              # Application logs
    └── uav_data/          # Processed UAV data
```

## Error Handling

- All operations use `@safe_operation` decorator for unified error handling
- Logging configured per-session in output directory
- Custom exceptions defined in `src/autoreport/exceptions.py`
- Graceful degradation for optional features (like manual sampling data)