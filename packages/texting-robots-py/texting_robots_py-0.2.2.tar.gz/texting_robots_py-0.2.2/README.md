# texting-robots-py

Python binding for the [Texting Robots](https://github.com/Smerity/texting_robots) `robots.txt` parser.
Refer to that project for details.

```
pip install texting-robots-py
```

## Usage

```python
from texting_robots import Robot

txt = b'''
User-Agent: FerrisCrawler
Allow: /ocean
Disallow: /rust
Disallow: /forest*.py
Crawl-Delay: 10
User-Agent: *
Disallow: /
Sitemap: https://www.example.com/site.xml
'''

robot = Robot('FerrisCrawler', txt)

assert robot.delay == 10

assert robot.sitemaps == ['https://www.example.com/site.xml']

assert robot.allowed('https://www.rust-lang.org/ocean')
assert robot.allowed('/ocean')
assert robot.allowed('/ocean/reef.html')
assert not robot.allowed('/rust')
assert not robot.allowed('/forest/tree/snake.py')
```

## Version numbering

The version of this project will equal the version of Texting Robots it depends on. For example, version 0.2.2 of `texting-robots-py` depends on version 0.2.2 of the `texting_robots` crate.

If necessary, this project will use [post releases](https://packaging.python.org/en/latest/specifications/version-specifiers/#post-releases) for changes specific to the Python package.

## Licence

This project is licensed under both the Apache 2.0 and MIT licences.
