# langcode_turner

A tool to turn language code version to other language code version.

e.g.

ISO 639-1 to ISO 639-3.

en -> eng

or

ISO 639-3 to ISO 639-1

est -> et

## Support language code and Version

- ISO 639-1
- ISO 639-2
- ISO 639-3
- Baidu language code
- Ids language code (The Intercontinental Dictionary Series)

# Usage

## install
```
pip install langcode_turner
```

## use
```python
from langcode_turner import langcode_turner

langcode = langcode_turner("est")
print(langcode.iso_639_3)

```

# update log

- v0.0.1 build code
- v0.0.2 - v0.0.6 fix error
- v0.0.6 a normal version
- v0.0.7 add baidu langcode
- v0.0.8-9 add ids language code support
- v0.1.0 change some function name and add unittest
- v0.1.1-2 fix a ids_id error, the ids_id type change to str.
- v0.1.3 fix a bug, add ci/cd gitlab
- v0.1.4 fix a language name can't find out code bug.
- v0.1.5 fix a bug, add language code name.
- v0.1.6 fix a bug, add language code name，add wordnet().
- v0.1.9 rebuild the code, fix a bug, add search_languages() method.
# License
MIT License

# Author
Feliks Peegel

