# bashrange

Bash range expression evaluator for your cli application

# Install

```bash
pip install bashrange
```

# Use

Import and call `expand_args`

```python
import argparse
from bashrange import expand_args
parser = argparse.ArgumentParser(prog="copy")
parser.add_argument("src", nargs='+')
parser.add_argument("dst")
args = parser.parse_args(expand_args())
```

And you can use bash range and list expressions outiside bash shell, for example on windows

```bash
python copy.py image{1..10}.jpg folder
python copy.py file.txt{,.bak}
```

## Author

Stanislav Doronin <mugisbrows@gmail.com>

## License

`bashrange` is distributed under the terms of MIT license, check `LICENSE` file.
