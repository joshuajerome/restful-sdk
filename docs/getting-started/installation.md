# Installation

## From PyPI (recommended)

```bash
pip install restful-sdk
```

## From GitHub Releases

Download the latest wheel from [GitHub Releases](https://github.com/joshuajerome/restful-sdk/releases):

```bash
pip install restful_sdk-0.0.1-py3-none-any.whl
```

## From Source (development)

```bash
git clone https://github.com/joshuajerome/restful-sdk.git
cd restful-sdk
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
