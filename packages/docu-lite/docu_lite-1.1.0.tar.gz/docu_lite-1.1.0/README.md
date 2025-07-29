# 🧾 docu-lite [![PyPI Downloads](https://static.pepy.tech/badge/docu-lite)](https://pepy.tech/projects/docu-lite)

### ⚡ Ultra-light Zero-dependency HTML outline generator for Python.   



- 📖   Browse classes and functions with collapsible docstrings in a tidy, readable format
- 📘   Specify your own stylesheet(s) or rely on the default (will be generated on run) 
- 🎈   No dependencies, short script
- ⚙️   [Integrate into your GitHub Workflow](https://g1ojs.github.io/docu-lite/add-to-workflow/index.html) to have automatically up-to-date outline(s) in your repo
- 👀   [Example live output:](https://g1ojs.github.io/docu-lite/docu-lite-outline.html)
- 👀   [Example live output (documentation mode):](https://g1ojs.github.io/docu-lite/docu-lite-outline-docmode.html)
  

## 🛠 Installation

Install using pip: open a command window and type

```
pip install docu-lite
```
## 💡 Usage
Either edit and run docu-lite.py in an IDE, or run from the command line:
```
docu-lite                         # uses or creates docu-lite.ini
docu-lite --config alt.ini        # uses alt.ini, errors if missing
```
Docu-lite will create a docu-lite.ini file if one doesn't exist.

⚙️ Edit the docu-lite.ini file to control how docu-lite runs:
 - **pattern** specifies where to look for input
 - **html** specifies the name of the output html file
 - **css** specifies the name of the input style sheet, which will be referenced from the output html file
 - **documentation_mode** produces a less detailed output styled for use as or editing into documentation. This mode uses a **completely separate stylesheet**, which can be tailored independently.
 - **ignore_docstrings_with** can be followed by = word to ignore docstrings containing the word (e.g. License, useful to stop license blocks appearing in the output)  


📝 If the specified css file is not found, docu-lite will generate one and reference it in the html

[PyPI link](https://pypi.org/project/docu-lite/)
