# @index-begin
# @symbol function/class: build L12
# @index-end
"""Trusted-code adapter example for an operator-supplied callable model. Index: docs/code-index.md.

Copy this factory, load your model once in build(), and implement answer(). Never load uploaded code.
"""

from server.ai import ExtractiveAdapter


def build():
    """Return the runnable offline reference adapter; replace it with a trusted local model wrapper."""
    return ExtractiveAdapter()
