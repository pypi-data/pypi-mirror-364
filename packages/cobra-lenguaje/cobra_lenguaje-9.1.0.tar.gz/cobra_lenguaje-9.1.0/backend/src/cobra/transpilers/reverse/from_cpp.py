# -*- coding: utf-8 -*-
"""Transpilador inverso desde C++ a Cobra usando tree-sitter."""

from backend.src.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromCPP(TreeSitterReverseTranspiler):
    LANGUAGE = "cpp"
