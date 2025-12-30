from src.core.btree import BTree

def test_delete_bug():
    print("--- Testing B-Tree Delete Bug (Fanout 3) ---")
    tree = BTree(fanout_n=3)
    
    # Reconstruct the tree from the screenshot
    # Insert keys to build the structure
    # Keys inferred from screenshot:
    # -1000, -100, -10, -1, 0, 1, 5, 6, 7, 10, 12, 17, 20, 30
    
    keys = [-1000, -100, -10, -1, 0, 1, 5, 6, 7, 10, 12, 17, 20, 30]
    
    print(f"Inserting keys: {keys}")
    for k in keys:
        tree.insert(k)
        
    print("\nTree State Before Delete:")
    for level in tree.to_levels():
        print(level)
        
    target = 6
    print(f"\nAttempting to delete {target}...")
    try:
        success = tree.delete(target)
        print(f"Delete success: {success}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

    print("\nTree State After Delete:")
    for level in tree.to_levels():
        print(level)

if __name__ == "__main__":
    test_delete_bug()
