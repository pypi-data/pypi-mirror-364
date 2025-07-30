"""Unfinished documentation feature based on pydoc-markdown."""

from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer

session = PydocMarkdown()
assert isinstance(session.loaders[0], PythonLoader)
session.loaders[0].search_path = ["./"]


assert isinstance(session.processors[0], FilterProcessor)
session.processors[0].documented_only = True
session.processors[0].do_not_filter_modules = False
session.processors[0].skip_empty_modules = True

assert isinstance(session.renderer, MarkdownRenderer)

session.renderer.render_toc = True
# session.renderer.render_toc_title = "ecmind_blue_client API"

modules = session.load_modules()
session.process(modules)


for module in modules:
    documentation = session.renderer.render_to_string([module])
    print(documentation)

    with open(f"docs/{module.name}.md", "w", encoding="utf-8") as file:
        file.write(documentation)
