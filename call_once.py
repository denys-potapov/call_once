#!/usr/bin/env python3
import sys
import ast


class ReturnTransformer(ast.NodeTransformer):
    def visit_Return(self, node):
        if node.value is not None:
            new_value = ast.Tuple(
                elts=[ast.Constant("result"), node.value], ctx=ast.Load()
            )
            return ast.Return(value=new_value)
        return node


class CallTransformer(ast.NodeTransformer):
    """Find recursive calls to the same function and replace them with variables."""

    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.assignments = []  # (var_name, call_node, parent_node)
        self.parent_stack = []

    def generic_visit(self, node):
        self.parent_stack.append(node)
        new_node = super().generic_visit(node)
        self.parent_stack.pop()
        return new_node

    def visit_Call(self, node):
        self.generic_visit(node)

        if isinstance(node.func, ast.Name) and node.func.id == self.name:
            var_name = f"{self.name}_{self.counter}"
            self.counter += 1

            parent = self.find_closest_parent((ast.If, ast.Return))
            self.assignments.append((var_name, node, parent))

            return ast.Name(id=var_name, ctx=ast.Load())
        return node

    def find_closest_parent(self, types):
        for n in reversed(self.parent_stack):
            if isinstance(n, types):
                return n
        return None


class NodeTransformerThatReturnsList(ast.NodeTransformer):
    """
    A NodeTransformer that can flatten nested statement lists.
    Only expands lists when visiting lists of statements, not single fields.
    """

    def visit_list(self, nodes):
        """Visit a list of nodes and flatten if any return lists."""
        new_body = []
        for node in nodes:
            result = self.visit(node)
            if result is None:
                continue
            if isinstance(result, list):
                new_body.extend(result)
            else:
                new_body.append(result)
        return new_body


class AssignmentsTransformer(NodeTransformerThatReturnsList):
    def __init__(self, assignments):
        self.assignments = assignments

    def generic_visit(self, node):
        # Visit children normally
        node = super().generic_visit(node)

        # Find assignments that belong to this node
        matches = [
            (var, call) for var, call, parent in self.assignments if parent is node
        ]
        if not matches:
            return node

        new_nodes = [
            ast.Assign(
                targets=[ast.Name(id=var, ctx=ast.Store())],
                value=call,
            )
            for var, call in matches
        ]
        new_nodes.append(node)
        return new_nodes


def transform_body(body, func_name):
    # return
    transformer = ReturnTransformer()
    body = [transformer.visit(stmt) for stmt in body]

    call_trans = CallTransformer(func_name)
    new_body = [call_trans.visit(stmt) for stmt in body]
    ass_trans = AssignmentsTransformer(call_trans.assignments)
    lifted_body = []
    for stmt in new_body:
        result = ass_trans.visit(stmt)
        if isinstance(result, list):
            lifted_body.extend(result)
        else:
            lifted_body.append(result)
    return lifted_body


class CallOnceTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Only process functions decorated with @call_once
        if not any(
            isinstance(d, ast.Name) and d.id == "call_once" for d in node.decorator_list
        ):
            return node

        func_name = node.name
        aux_name = func_name + "_aux"
        cache_name = func_name + "_CACHE"

        # Remove @call_once decorator
        node.decorator_list = [
            d
            for d in node.decorator_list
            if not (isinstance(d, ast.Name) and d.id == "call_once")
        ]

        # Create auxiliary function
        aux_func = ast.FunctionDef(
            name=aux_name,
            args=node.args,
            body=transform_body(node.body, func_name),
            decorator_list=[],
            returns=node.returns,
            type_comment=None,
        )

        # Build the memoizing wrapper code as a string
        wrapper_code = f"""
{cache_name} = {{}}

def {func_name}(*args, **kwargs):
    key = (args, tuple(kwargs.items()))
    if key not in {cache_name}:
        {cache_name}[key] = {aux_name}(*args, **kwargs)
    return {cache_name}[key]
"""
        wrapper_ast = ast.parse(wrapper_code)

        # Return the new nodes (cache + wrapper + aux)
        return wrapper_ast.body + [aux_func]


def main():
    source = sys.stdin.read()

    tree = ast.parse(source)
    new_tree = CallOnceTransformer().visit(tree)
    ast.fix_missing_locations(new_tree)

    code = ast.unparse(new_tree)
    print(code)


if __name__ == "__main__":
    main()
