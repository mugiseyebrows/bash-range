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
parser = argparse.ArgumentParser(prog="copy.py")
parser.add_argument("src", nargs='+')
parser.add_argument("dst")
args = parser.parse_args(expand_args())
```

And you can use bash range and list expressions outiside bash shell, for example in cmd on windows

```bash
python copy.py image{1..10}.jpg folder
python copy.py file.txt{,.bak}
```

You can test expression expansion in cmd like this

```bash
python -m bashrange -v {1..10..2}
```

## Author

Stanislav Doronin <mugisbrows@gmail.com>

## License

`bashrange` is distributed under the terms of MIT license, check `LICENSE` file.
