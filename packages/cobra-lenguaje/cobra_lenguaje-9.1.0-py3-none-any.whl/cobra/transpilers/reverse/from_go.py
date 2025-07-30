# -*- coding: utf-8 -*-
"""Transpilador inverso desde Go a Cobra usando tree-sitter."""

from backend.src.cobra.transpilers.reverse.tree_sitter_base import TreeSitterReverseTranspiler


class ReverseFromGo(TreeSitterReverseTranspiler):
    LANGUAGE = "go"
