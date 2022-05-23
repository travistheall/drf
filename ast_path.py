"""
A class to parse python's abstract syntax tree in order to compare two
versions of the same package.
"""

import ast
from _ast import AST, Module
from pprint import pprint
from packaging import version
from typing import Dict, List, Union


class MyClassNode(object):
    """
    Properties
    ----------
    _file : protected property holding the file passed in
    veer : a Version object for ease of comparing package versions
    file_ast : the abstract syntax tree of the file passed in
    name : the class being searched
    node : the abstract syntax node of the class from the tile
    methods : parameters linked to the methods declared for that class
    meth_names : the method names alone
    """
    def __init__(self, file: str, ver: str, node_name: str) -> None:
        """
        Parameters
        ----------
        file : the file name
        ver : the version
        node_name : the class name that you wish to compare
        """
        self._file: str = file
        self.ver: version.Version = version.Version(ver)
        with open(file, "r") as f:
            self.file_ast: Union[AST, Module] = ast.parse(f.read())
        self.name: str = node_name
        self.node: ast.ClassDef = self.node()
        self.methods: Dict[str: List[str]] = {
            node.name: self.get_fn_args(node)
            for node in self.node.body
            if isinstance(node, ast.FunctionDef)
        }
        self.meth_names: List[str] = list(self.methods.keys())

    def node(self) -> ast.ClassDef:
        """
        Returns
        -------
            ast.ClassDef : node matching the requested node name
        """
        for node in self.file_ast.body:
            if isinstance(node, ast.ClassDef) and node.name == self.name:
                return node

    @staticmethod
    def get_fn_args(function_node: ast.FunctionDef) -> List[str]:
        """
        Parameters
        ----------
        function_node : the node from which you want to get the arguments

        Returns
        -------
            a list of the arguments passed in to the analyzed function
        """
        return [arg.arg for arg in function_node.args.args]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Node from AST path{self.name}"

    def __gt__(self, other_node) -> bool:
        return self.ver > other_node.ver

    def __ge__(self, other_node) -> bool:
        return self.ver >= other_node.ver

    def __lt__(self, other_node) -> bool:
        return self.ver < other_node.ver

    def __le__(self, other_node) -> bool:
        return self.ver <= other_node.ver

    def __ne__(self, other_node) -> bool:
        return self.ver != other_node.ver

    def __eq__(self, other_node) -> bool:
        return self.ver == other_node.ver

    def diff_methods(self, other_node) -> Dict[str: List[str]]:
        """
        Parameters
        ----------
        other_node : another MyNode object to compare against

        Returns
        -------
            a dictionary containing the functions added
            and removed since the compared version
        """
        older, newer = other_node, self
        if self > other_node:
            older, newer = self, other_node

        meths: Dict[str: List[str]] = {'added': [n for n in newer.meth_names if n not in older.meth_names],
                                       'removed': [n for n in older.meth_names if n not in newer.meth_names]}
        return meths


if __name__ == "__main__":
    schema9 = MyClassNode(file="drf394/rest_framework/schemas/generators.py", ver="3.9.4", node_name="SchemaGenerator")
    schema6 = MyClassNode(file="drf362/rest_framework/schemas.py", ver="3.6.2", node_name="SchemaGenerator")
    pprint(schema9.methods)
    pprint(schema6.diff_methods(schema9))
