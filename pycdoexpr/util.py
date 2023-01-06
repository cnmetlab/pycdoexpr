from binarytree import Node


def construct_tree(kw: list, cond: list) -> Node:
    """construct condition binary tree with keyword list and condition list

    Args:
        kw (list): keyword list
        cond (list): condition list

    Returns:
        Node: binary tree root node
    """
    if len(kw) == 2 and len(cond) == 1 and kw[0] == "if" and kw[1] == "else":
        left = Node(value=0)
        right = Node(value=1)
        root = Node(value=cond[0].value, left=left, right=right)
        return root
    else:
        stack = []
        for n, k in enumerate(kw):
            if k == "if":
                stack.append(n)
            elif k == "else":
                idx = stack.pop()
            if len(stack) == 0:
                if_index = idx
                else_index = n
                break

        root = Node(value=cond[if_index].value)

        if if_index + 1 == else_index:
            left = Node(0)
            right = construct_tree(kw[else_index + 1 :], cond[if_index + 1 :])
        elif if_index + 1 < else_index:
            cond_num = kw[if_index + 1 : else_index - 1].count("if")
            left = construct_tree(kw[if_index + 1 : else_index], cond[1 : cond_num + 1])
            if len(kw[else_index + 1 :]) <= 1:
                right = Node(1)
            else:
                right = construct_tree(kw[else_index + 1 :], cond[cond_num + 1 :])

        root.left = left
        root.right = right
        return root

def construct_tree_with_tree_nodes(nodes:dict)->Node:
    """construct condition binary tree with decision tree nodes dict

    Args:
        nodes (dict): decision tree node dictionary

    Returns:
        Node: binary tree node
    """

    def _construct_xgb_tree_node(root_number:int)->Node:
        n = nodes[root_number]
        root = Node(n.value)
        if len(n.child_number):
            left, right = _construct_xgb_tree_node(n.child_number[0]), _construct_xgb_tree_node(n.child_number[1])
            root.left, root.right = left, right
        return root
            
    root = _construct_xgb_tree_node(0)
    return root

def get_max_min_leaf_depth(root: Node) -> tuple:
    """get max min leaf depth from root

    Args:
        root (Node): _description_

    Returns:
        tuple: max_leaf_depth, min_leaf_depth
    """

    size = 0
    leaf_count = 0
    min_leaf_depth = 0
    max_leaf_depth = -1
    is_strict = True
    current_nodes = [root]

    while len(current_nodes) > 0:
        max_leaf_depth += 1
        next_nodes = []
        for node in current_nodes:
            size += 1
            # Node is a leaf.
            if node.left is None and node.right is None:
                if min_leaf_depth == 0:
                    min_leaf_depth = max_leaf_depth
                leaf_count += 1

            if node.left is not None:

                next_nodes.append(node.left)

            if node.right is not None:

                next_nodes.append(node.right)

            # If we see a node with only one child, it is not strict
            is_strict &= (node.left is None) == (node.right is None)
        current_nodes = next_nodes
    return max_leaf_depth, min_leaf_depth

def construct_expr(node: Node) -> str:
    """construct cdo condition expr from binary tree root node

    Args:
        node (Node): root node

    Returns:
        str: expr str
    """
    patt = "(({condition}))? ({true_value}): ({false_value})"
    if get_max_min_leaf_depth(node)[0] == 1:
        res = patt.format(
            condition=node.value,
            true_value=node.left.value.split("=")[-1],
            false_value=node.right.value.split("=")[-1],
        )
        return res
    else:
        if get_max_min_leaf_depth(node.left)[0] >= 1:
            left = construct_expr(node.left)
        else:
            left = node.left.value.split("=")[-1]
        if get_max_min_leaf_depth(node.right)[0] >= 1:
            right = construct_expr(node.right)
        else:
            right = node.right.value.split("=")[-1]
        res = patt.format(condition=node.value, true_value=left, false_value=right)
        return res
