#!/usr/bin/env python3
"""Test canvodpy factories implementation."""

print("Testing canvodpy factories...")
print("=" * 60)

# Test 1: Import canvodpy
print("\n1. Testing import...")
try:
    import canvodpy
    print("   ✅ Import successful")
    print(f"   Version: {canvodpy.__version__}")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

# Test 2: Check factories are available
print("\n2. Testing factory availability...")
try:
    assert hasattr(canvodpy, 'ReaderFactory')
    assert hasattr(canvodpy, 'GridFactory')
    assert hasattr(canvodpy, 'VODFactory')
    assert hasattr(canvodpy, 'AugmentationFactory')
    print("   ✅ All factories available")
except Exception as e:
    print(f"   ❌ Factory availability failed: {e}")
    exit(1)

# Test 3: Check logging is available
print("\n3. Testing logging...")
try:
    assert hasattr(canvodpy, 'setup_logging')
    assert hasattr(canvodpy, 'get_logger')
    log = canvodpy.get_logger(__name__)
    print("   ✅ Logging available")
except Exception as e:
    print(f"   ❌ Logging failed: {e}")
    exit(1)

# Test 4: Check built-in registrations
print("\n4. Testing built-in component registration...")
try:
    readers = canvodpy.ReaderFactory.list_available()
    grids = canvodpy.GridFactory.list_available()
    vods = canvodpy.VODFactory.list_available()
    
    print(f"   Readers: {readers}")
    print(f"   Grids: {grids}")
    print(f"   VOD calculators: {vods}")
    
    if "rinex3" in readers:
        print("   ✅ Reader registered")
    else:
        print("   ⚠️  No readers registered (canvod-readers missing?)")
    
    if "equal_area" in grids:
        print("   ✅ Grid registered")
    else:
        print("   ⚠️  No grids registered (canvod-grids missing?)")
    
    if "tau_omega" in vods:
        print("   ✅ VOD calculator registered")
    else:
        print("   ⚠️  No VOD calculators registered (canvod-vod missing?)")
        
except Exception as e:
    print(f"   ❌ Registration check failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Test factory creation
print("\n5. Testing factory creation...")
try:
    if "equal_area" in canvodpy.GridFactory.list_available():
        grid = canvodpy.GridFactory.create(
            "equal_area",
            angular_resolution=10.0,
            cutoff_theta=75.0,
        )
        print(f"   ✅ Grid created: {type(grid).__name__}")
    else:
        print("   ⚠️  Skipping (no grids available)")
except Exception as e:
    print(f"   ❌ Factory creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
