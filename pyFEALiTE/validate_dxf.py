"""
DXF File Validation Script
==========================

This script validates that the generated DXF files are properly formatted
and can be read by ezdxf library.
"""

import ezdxf
from pathlib import Path

def validate_dxf_file(filename):
    """Validate a DXF file and report its contents."""
    try:
        doc = ezdxf.readfile(filename)
        print(f"\n✅ {filename} - Valid DXF file")
        print(f"   Format: {doc.dxfversion}")
        print(f"   Layers: {len(doc.layers)} layers")
        print(f"   Entities: {len(list(doc.modelspace()))} entities")
        
        # List layers
        layer_names = [layer.dxf.name for layer in doc.layers]
        print(f"   Layer names: {', '.join(layer_names[:5])}...")
        
        # Count entity types
        entity_types = {}
        for entity in doc.modelspace():
            entity_type = entity.dxftype()
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print(f"   Entity types: {dict(list(entity_types.items())[:3])}...")
        
        return True
        
    except Exception as e:
        print(f"❌ {filename} - Error: {e}")
        return False

def main():
    """Validate all DXF files in the current directory."""
    print("🔍 Validating DXF Files")
    print("=" * 50)
    
    dxf_files = list(Path('.').glob('*.dxf'))
    
    if not dxf_files:
        print("No DXF files found in current directory")
        return
    
    valid_count = 0
    total_count = len(dxf_files)
    
    for dxf_file in dxf_files:
        if validate_dxf_file(dxf_file):
            valid_count += 1
    
    print(f"\n📊 Validation Summary")
    print("=" * 50)
    print(f"✅ Valid files: {valid_count}/{total_count}")
    print(f"📁 Total size: {sum(f.stat().st_size for f in dxf_files) / 1024:.1f} KB")
    
    if valid_count == total_count:
        print("🎉 All DXF files are valid and ready for CAD import!")
    else:
        print("⚠️  Some DXF files have issues")

if __name__ == "__main__":
    main()
