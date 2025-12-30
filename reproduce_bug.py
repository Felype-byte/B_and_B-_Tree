from src.core.btree import BTree

def test_btree_bug():
    # Helper to print tree
    def print_tree(btree):
        levels = btree.to_levels()
        for i, level in enumerate(levels):
            print(f"Level {i}: {level}")

    print("--- Testing B-Tree with Fanout 3 ---")
    tree = BTree(fanout_n=3)
    
    # Operations from user
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    
    for k in keys:
        print(f"\nInserting {k}...")
        tree.insert(k)
        print_tree(tree)
        
        # Check for empty nodes in children
        for node in tree.get_all_nodes():
            if len(node.keys) == 0 and node != tree.root:
                print(f"CRITICAL: Found non-root empty node! ID: {node.id}")

if __name__ == "__main__":
    test_btree_bug()
