# Installation

## From GitHub Releases (recommended)

Download the latest wheel from [GitHub Releases](https://github.com/joshuajerome/restful/releases):

```bash
pip install restful-0.1.0-py3-none-any.whl
```

Or install directly from the release URL:

```bash
pip install https://github.com/joshuajerome/restful/releases/download/v0.1.0/restful-0.1.0-py3-none-any.whl
```

## From Source (development)

```bash
git clone https://github.com/joshuajerome/restful.git
cd restful
uv sync
```

## Verify Installation

```bash
python -c "from restful import Client; print('restful OK')"
```

Or using the CLI:

```bash
python -m restful --help
```

## Requirements

- Python >= 3.10
- Dependencies: `requests`, `urllib3`, `pyyaml` (installed automatically)
