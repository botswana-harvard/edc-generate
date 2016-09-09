from django import template

from bs4 import BeautifulSoup
from markdown import markdown
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name, guess_lexer

register = template.Library()


@register.filter
def render(content, safe="unsafe"):
    """Render this content for display."""

    # First, pull out all the <code></code> blocks, to keep them away
    # from Markdown (and preserve whitespace).
    soup = BeautifulSoup(str(content))
    code_blocks = soup.findAll('code')
    for block in code_blocks:
        block.replaceWith('<code class="removed"></code>')

    # Run the post through markdown.
    if safe == "unsafe":
        safe_mode = False
    else:
        safe_mode = True
    markeddown = markdown(str(soup), safe_mode=safe_mode)

    # Replace the pulled code blocks with syntax-highlighted versions.
    soup = BeautifulSoup(markeddown)
    empty_code_blocks, index = soup.findAll('code', 'removed'), 0
    formatter = html(cssclass='source')
    for block in code_blocks:
        if 'class' in block:
            # <code class='python'>python code</code>
            language = block['class']
        else:
            # <code>plain text, whitespace-preserved</code>
            language = 'text'
        try:
            lexer = get_lexer_by_name(language, stripnl=True, encoding='UTF-8')
        except ValueError:
            try:
                # Guess a lexer by the contents of the block.
                lexer = guess_lexer(block.renderContents())
            except ValueError:
                # Just make it plain text.
                lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
        empty_code_blocks[index].replaceWith(
            highlight(block.renderContents(), lexer, formatter))
        index = index + 1

    return str(soup)
