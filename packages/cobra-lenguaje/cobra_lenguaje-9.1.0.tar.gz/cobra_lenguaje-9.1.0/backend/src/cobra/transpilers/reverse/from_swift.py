# -*- coding: utf-8 -*-
"""Transpilador inverso desde Swift a Cobra usando tree-sitter."""

from backend.src.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromSwift(TreeSitterReverseTranspiler):
    LANGUAGE = "swift"
