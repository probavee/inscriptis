#!/usr/bin/env python
# encoding: utf-8

"""
Elements used for rendering (parts) of the canvas.

The :class:`Canvas` represents the drawing board to which the HTML page
is serialized.
"""
from html import unescape

from inscriptis.annotation import Annotation
from inscriptis.html_properties import WhiteSpace
from inscriptis.model.block import Block
from inscriptis.model.html_element import HtmlElement
from inscriptis.model.prefix import Prefix


class Canvas:
    """
    The text Canvas on which Inscriptis writes the HTML page.

    Attributes:
        margin: the current margin to the previous block (this is required to
                ensure that the `margin_after` and `margin_before` constraints
                of HTML block elements are met).
        current_block: A list of TextSnippets that will be consolidated into a
                       block, once the current block is completed.
        blocks: a list of finished blocks (i.e., text lines)
        annotations: the list of completed annotations
        annotation_counter: a counter used for enumerating all annotations
                            we encounter.
    """

    __slots__ = ('annotations', 'blocks', 'current_block',
                 'margin', 'annotation_counter')

    def __init__(self):
        """
        Contains the completed blocks. Each block spawns at least a line
        """
        self.margin = 1000  # margin to the previous block
        self.current_block = Block(0, Prefix())
        self.blocks = []
        self.annotations = []
        self.annotation_counter = {}

    def open_block(self, tag: HtmlElement):
        """
        Opens an HTML block element.
        """
        self._flush_inline()
        self.current_block.prefix.register_prefix(tag.padding_inline,
                                                  tag.list_bullet)

        # write the block margin
        required_margin = max(tag.previous_margin_after, tag.margin_before)
        if required_margin > self.margin:
            self.blocks.append('\n' * (required_margin - self.margin - 1))
            self.margin = required_margin

    def write(self, tag: HtmlElement, text: str,
              whitespace: WhiteSpace = None):
        """
        Writes the given block.
        """
        span = self.current_block.merge(text, whitespace or tag.whitespace)

        if tag.annotation and span.start != span.end:
            for annotation in tag.annotation:
                self.annotations.append(
                    Annotation(span.start, span.end, text, annotation))

    def close_block(self, tag: HtmlElement):
        """
        Closes the given HtmlElement by writing its bottom margin.

        Args:
            tag: the HTML Block element to close
        """
        self._flush_inline()
        self.current_block.prefix.remove_last_prefix()
        if tag.margin_after > self.margin:
            self.blocks.append('\n' * (tag.margin_after - self.margin - 1))
            self.margin = tag.margin_after

    def write_newline(self):
        if not self._flush_inline():
            self.blocks.append('')
            self.current_block = self.current_block.new_block()

    def get_text(self) -> str:
        """
        Provide a text representation of the current block
        """
        self._flush_inline()
        return unescape('\n'.join((block.rstrip(' ')
                                   for block in self.blocks)))

    def _flush_inline(self) -> bool:
        """
        Attempts to flush the content in self.current_block into a new block
        which is added to self.blocks.

        If self.current_block does not contain any content (or only
        whitespaces) no changes are made.

        Returns: True if the attempt was successful, False otherwise.
        """
        if not self.current_block.is_empty():
            self.blocks.append(self.current_block.content)
            self.current_block = self.current_block.new_block()
            self.margin = 0
            return True

        return False
