
import sys
import os
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import BTree, BPlusTree, Tracer, Metrics, validate_btree, validate_bplustree, ValidationError

def test_tree(tree_class, tree_name, validator):
    print(f"\n{'='*80}")
    print(f"TESTING: {tree_name}")
    print(f"{'='*80}")
    
    tracer = Tracer()
    tracer.disable() # Speed up
    tree = tree_class(fanout_n=3, tracer=tracer) # Low fanout to force splits
    
    # 1. INSERTION TEST
    print("1. Insertion Test (Sequential 1-20)")
    keys = list(range(1, 21))
    for k in keys:
        tree.insert(k)
        
    try:
        validator(tree)
        print("   [PASS] Validation after insertion")
    except ValidationError as e:
        print(f"   [FAIL] Validation error: {e}")
        return False

    if len(tree.get_all_nodes()) > 1:
        print("   [PASS] Tree grew in height/nodes")
    else:
        print("   [FAIL] Tree did not grow as expected")
        return False

    # 2. SEARCH TEST
    print("2. Search Test")
    found_all = True
    for k in keys:
        if not tree.search(k)['found']:
            found_all = False
            print(f"   [FAIL] Key {k} not found")
            break
    if found_all:
        print("   [PASS] All keys found")

    # 3. REMOVAL TEST
    print("3. Removal Test (Random 10 keys)")
    # Remove half the keys randomly
    random.shuffle(keys)
    keys_to_remove = keys[:10]
    keys_to_keep = keys[10:]
    
    print(f"   Removing: {keys_to_remove}")
    
    for k in keys_to_remove:
        tree.delete(k)
        
    try:
        validator(tree)
        print("   [PASS] Validation after removal")
    except ValidationError as e:
        print(f"   [FAIL] Validation error after removal: {e}")
        return False

    # Verify removed keys are gone
    gone_all = True
    for k in keys_to_remove:
        if tree.search(k)['found']:
            gone_all = False
            print(f"   [FAIL] Key {k} still exists!")
            break
            
    # Verify kept keys are still there
    kept_all = True
    for k in keys_to_keep:
        if not tree.search(k)['found']:
            kept_all = False
            print(f"   [FAIL] Key {k} lost!")
            break
            
    if gone_all and kept_all:
        print("   [PASS] Keys correctly removed/kept")
        return True
    else:
        return False

def main():
    print("STARTING FINAL VALIDATION...")
    
    btree_ok = test_tree(BTree, "Standard B-Tree", validate_btree)
    bplus_ok = test_tree(BPlusTree, "B+ Tree", validate_bplustree)
    
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"B-Tree:  {'PASS' if btree_ok else 'FAIL'}")
    print(f"B+ Tree: {'PASS' if bplus_ok else 'FAIL'}")
    
    if btree_ok and bplus_ok:
        print("\nALL SYSTEMS GO! 🚀")
        return 0
    else:
        print("\nSYSTEM FAILURE ❌")
        return 1

if __name__ == "__main__":
    sys.exit(main())
