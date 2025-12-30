from src.core.btree import BTree, BTreeNode

def build_scenario():
    tree = BTree(fanout_n=3)
    
    # Root
    root = BTreeNode(is_leaf=False)
    root.keys = [110, 679]
    tree.root = root
    
    # Layer 1
    n39 = BTreeNode(is_leaf=False)
    n39.keys = [39]
    
    n600 = BTreeNode(is_leaf=False)
    n600.keys = [600]
    
    n735 = BTreeNode(is_leaf=False)
    n735.keys = [735, 883]
    
    root.children = [n39, n600, n735]
    
    # Layer 2 (Leaves)
    l32 = BTreeNode(is_leaf=True); l32.keys = [32]
    l92 = BTreeNode(is_leaf=True); l92.keys = [92]
    n39.children = [l32, l92]
    
    l298 = BTreeNode(is_leaf=True); l298.keys = [298]
    l623 = BTreeNode(is_leaf=True); l623.keys = [623]
    n600.children = [l298, l623]
    
    l698 = BTreeNode(is_leaf=True); l698.keys = [698]
    l847 = BTreeNode(is_leaf=True); l847.keys = [847]
    l888 = BTreeNode(is_leaf=True); l888.keys = [888]
    n735.children = [l698, l847, l888]
    
    return tree

def test_delete():
    tree = build_scenario()
    print("Initial Tree:")
    for l in tree.to_levels(): print(l)
    
    print("\nRemoving 600...")
    success = tree.delete(600)
    print(f"Delete returned: {success}")
    
    print("\nFinal Tree:")
    for l in tree.to_levels(): print(l)

if __name__ == "__main__":
    test_delete()
