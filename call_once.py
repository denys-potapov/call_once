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

            parent = self.find_closest_parent()
            self.assignments.append((var_name, node, parent))

            return ast.Name(id=var_name, ctx=ast.Load())
        return node

    def find_closest_parent(self):
        valid_types = (
            ast.If,
            ast.Return,
            ast.Assign,
            ast.AnnAssign,
            ast.AugAssign,
            ast.Expr,
        )
        for n in reversed(self.parent_stack):
            if isinstance(n, valid_types):
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
    def __init__(self, assignments, cache_name):
        self.assignments = assignments
        self.cache_name = cache_name

    def generic_visit(self, node):
        node = super().generic_visit(node)

        matches = [
            (var, call) for var, call, parent in self.assignments if parent is node
        ]
        if not matches:
            return node

        new_nodes = []
        for var, call in matches:
            # Build args as comma-separated source
            args_src = ""
            if call.args:
                args_src = "".join(f"{ast.unparse(a)}, " for a in call.args)

            # Build kwargs as tuple of (key, value) pairs
            kwargs_src = ""
            if call.keywords:
                kwargs_src = "".join(
                    f"('{kw.arg}', {ast.unparse(kw.value)}), " for kw in call.keywords
                )

            key_var = f"{var}_args"

            template = f"""
{key_var} = (({args_src}), ({kwargs_src}))
if {key_var} not in {self.cache_name}:
    return ("call", {key_var})
{var} = {self.cache_name}[{key_var}]
            """

            parsed = ast.parse(template).body
            new_nodes.extend(parsed)

        new_nodes.append(node)
        return new_nodes


def transform_body(body, func_name, cache_name):
    # return
    transformer = ReturnTransformer()
    body = [transformer.visit(stmt) for stmt in body]

    call_trans = CallTransformer(func_name)
    body = [call_trans.visit(stmt) for stmt in body]
    body = AssignmentsTransformer(call_trans.assignments, cache_name).visit_list(body)

    return body


class CallOnceTransformer(ast.NodeTransformer):
    def header_ast(self):
        return ast.parse("""
def call_once(fn, args, cache):
    stack = {}

    def push(args):
        stack[args] = None

    def pop():
        return stack.popitem()[0]

    push(args)
    while len(stack) > 0:
        current_args = pop()
        if current_args in cache:
            continue
        (posargs, kwargs) = current_args
        (typ, value) = fn(*posargs, **dict(kwargs))
        if typ == "call":
            push(current_args)
            push(value)
            continue
        if typ == "result":
            cache[current_args] = value
    return cache[args]""").body

    def visit_FunctionDef(self, node):
        if node.name == "call_once":
            return self.header_ast()

        self.generic_visit(node)

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
            body=transform_body(node.body, func_name, cache_name),
            decorator_list=[],
            returns=node.returns,
            type_comment=None,
        )

        # Build the memoizing wrapper code as a string
        wrapper_code = f"""
{cache_name} = {{}}

def {func_name}(*posargs, **kwargs):
    args = (posargs, tuple(kwargs.items()))
    return call_once({aux_name}, args, {cache_name})
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
