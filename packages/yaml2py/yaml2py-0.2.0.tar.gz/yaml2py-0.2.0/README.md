# yaml2py

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/yaml2py.svg)](https://badge.fury.io/py/yaml2py)

A CLI tool to generate type-hinted Python config classes from YAML files with nested structure support, automatic file watching and hot reloading capabilities.

## Features

- 🔧 **Auto-generate type-hinted Python classes** from YAML configuration files
- 🏗️ **Nested structure support** - handle complex YAML hierarchies with ease
- 🔍 **Intelligent type inference** (int, float, boolean, string, list, dict)
- 🔄 **Hot reloading** - automatically reload configuration when files change
- 🛡️ **Sensitive data masking** - automatically hide passwords and API keys
- 🎯 **Smart path detection** - automatically find config files in common locations
- 💡 **IDE-friendly** - full autocomplete and type hints support
- 🚀 **Singleton pattern** - ensure single configuration instance across your app

## Installation

```bash
pip install yaml2py
```

## Quick Start

### 1. Create a config.yaml file

```yaml
system:
  mode: development
  debug: true
  port: 8080
  timeout: 30.5

database:
  host: localhost
  port: 5432
  name: myapp
  user: admin
  password: secret123
  options:
    pool_size: 10
    retry_attempts: 3

redis:
  host: 127.0.0.1
  port: 6379
  db: 0

features:
  - name: authentication
    enabled: true
    config:
      session_timeout: 3600
      max_attempts: 5
  - name: logging
    enabled: false
    config:
      level: info
      format: json

ai_service:
  api_key: sk-1234567890abcdef
  model: gpt-4
  endpoints:
    - path: /chat
      method: POST
      rate_limit: 100
    - path: /completions
      method: POST
      rate_limit: 50
```

### 2. Generate Python config classes

```bash
yaml2py --config config.yaml --output ./src/config
```

Or use it interactively (auto-detects config files):

```bash
yaml2py
```

### 3. Use in your code

```python
from src.config.manager import ConfigManager

# Get singleton instance
config = ConfigManager()

# Access with full type hints and autocomplete
print(config.system.mode)            # 'development'
print(config.system.debug)           # True (as boolean)
print(config.database.port)          # 5432 (as int)
print(config.system.timeout)         # 30.5 (as float)

# Access nested structures
print(config.database.options.pool_size)      # 10
print(config.database.options.retry_attempts) # 3

# Access lists with type safety
for feature in config.features:
    print(f"{feature.name}: {feature.enabled}")
    if feature.enabled:
        print(f"  Timeout: {feature.config.session_timeout}")

# Direct access returns actual values
print(config.database.password)      # 'secret123'
print(config.ai_service.api_key)     # 'sk-1234567890abcdef'

# Use print_all() method to safely display config with masked sensitive data
config.database.print_all()
# Output:
# DatabaseSchema:
# ----------------------------------------
#   host: localhost
#   port: 5432
#   name: myapp
#   user: admin
#   password: se*****23  # Automatically masked!
# ----------------------------------------

# Hot reloading - config updates automatically
# Edit config.yaml and changes are reflected immediately!
```

## Advanced Features

### Nested Structure Support

yaml2py excels at handling complex nested structures:

```yaml
app:
  name: MyApp
  services:
    cache:
      provider: redis
      settings:
        ttl: 3600
        max_entries: 1000
    queue:
      provider: rabbitmq
      settings:
        prefetch: 10
        durable: true
```

Access nested values with full type safety:

```python
config.app.services.cache.settings.ttl  # Full IDE support!
```

### List Handling

Automatically generates typed classes for lists of objects:

```yaml
servers:
  - name: web-1
    host: 10.0.0.1
    port: 80
  - name: web-2
    host: 10.0.0.2
    port: 80
```

```python
for server in config.servers:
    # server has full type hints
    print(f"{server.name}: {server.host}:{server.port}")
```

### Hot Reloading

Configuration automatically reloads when files change:

```python
# Start your app
config = ConfigManager()
print(config.system.debug)  # False

# Edit config.yaml and set debug: true
# No restart needed!
print(config.system.debug)  # True
```

### Type Safety

All configurations are properly typed:

```python
config.system.debug          # bool
config.database.port         # int
config.system.timeout        # float
config.database.name         # str
config.features              # List[FeatureSchema]
config.database.options      # OptionsSchema
```

## CLI Options

```bash
yaml2py --help

Options:
  -c, --config PATH   Path to YAML configuration file
  -o, --output PATH   Output directory for generated files
  --help             Show this message and exit
```

## Generated File Structure

```
output_dir/
├── __init__.py      # Package initialization
├── schema.py        # Configuration classes with type hints
└── manager.py       # Singleton manager with hot reload
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Quality

```bash
make lint    # Run linting
make format  # Format code
make test    # Run tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## TODO

- [ ] Support for custom type validators
- [ ] YAML anchors and references
- [ ] Environment variable interpolation
- [ ] Multiple config file merging
- [ ] Config inheritance