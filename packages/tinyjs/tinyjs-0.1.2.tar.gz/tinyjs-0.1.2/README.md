# TinyJS

A simple package that allows for synthesising simple, syntaxically correct, javascript code

## Installation
```bash
pip install tinyjs
```

## Usage
```python
from tinyjs import create_program, annotate_program

program_list = create_program(level="ALL", count=1000)
annotated_program_list = annotate_program(program_list, level="ALL")
# Or
annotated_program_list = create_program(level="ALL", count=1000, annotated=True)
```

> Note: Annotation requires NodeJS to be installed! Annotation happens by evaluating the code, and for reliability, this was handled by native NodeJS instead

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Acknowledgements
This project is a modified port of the TinyJS generator by Kamel Yamani et al., 2021
- [Link to the github page of the project](https://github.com/MarwaNair/TinyPy-Generator)
- [Link to the research paper](https://doi.org/10.48550/arXiv.2403.06503)