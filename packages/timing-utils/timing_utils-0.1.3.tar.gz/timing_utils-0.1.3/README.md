# timing-utils

Simple utilities to time the execution of synchronous and asynchronous Python functions.

## Installation

```bash
pip install timing-utils
```

## Usage

```python
from timing_utils import timeit, async_timeit

@timeit
def fast_func():
    return sum(range(10000))

@async_timeit
async def slow_async_func():
    import asyncio
    await asyncio.sleep(1)

# Example of running the async function (in an async environment):
# await slow_async_func()
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests if needed
4. Run tests locally: `make test`
5. Submit a pull request

Please follow the existing coding style and include relevant documentation if applicable.

## License

This project is licensed under the [MIT License](LICENSE).