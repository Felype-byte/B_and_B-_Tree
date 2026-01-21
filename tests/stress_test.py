
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import BTree, BPlusTree, Tracer

def print_tree(tree, label):
    print(f"\n--- {label} ---")
    for lvl in tree.to_levels():
        print(f"  {' '.join(lvl)}")

def stress_test(tree_cls, name):
    print(f"\n{'#'*60}")
    print(f"STRESS TEST: {name} (Fanout=3)")
    print(f"{'#'*60}")
    
    # Fanout 3 forces splits every 2 keys
    tree = tree_cls(fanout_n=3)
    
    print("\n[PHASE 1] EXPLOSIVE GROWTH (Insert 1-15)")
    # This will force the tree to grow to height 3 or 4 quickly
    for i in range(1, 16):
        tree.insert(i)
    print_tree(tree, "After Insertion 1-15")
    
    print("\n[PHASE 2] CORE DESTRUCTION (Remove Key Nodes)")
    
    # Remove Root/Pivot candidates to force complex merges
    targets = [8, 4, 12, 2, 6, 10, 14] 
    print(f"Removing pivots: {targets}")
    
    for k in targets:
        tree.delete(k)
        
    print_tree(tree, "After Removing Pivots")
    
    print("\n[PHASE 3] TOTAL WIPEOUT (Remove Remaining)")
    # Remove everything else to ensure no 'ghost' pointers remain
    remaining = [k for k in range(1, 16) if k not in targets]
    print(f"Removing rest: {remaining}")
    
    for k in remaining:
        tree.delete(k)
        
    print_tree(tree, "Empty Tree?")
    
    if len(tree.get_all_nodes()) <= 1 and len(tree.root.keys) == 0:
         print("\n>>> SURVIVED! Tree is clean and valid.")
    else:
         print("\n>>> FAILED! Tree has zombies.")

if __name__ == "__main__":
    stress_test(BTree, "Standard B-Tree")
    stress_test(BPlusTree, "B+ Tree")
