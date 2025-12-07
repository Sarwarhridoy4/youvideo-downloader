"""
Create proper icon files for all platforms from a single PNG source.
Run this to generate appicon.ico, appicon.icns, and various sizes.

Usage:
    python create_icon.py assets/icons/appicon.png
"""

import sys
from pathlib import Path
from PIL import Image


def create_ico_file(png_path: Path, output_path: Path):
    """Create a proper Windows .ico file with multiple sizes."""
    print(f"\n📦 Creating ICO file...")
    
    img = Image.open(png_path)
    
    # Ensure RGBA mode for transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Windows needs these specific sizes for taskbar
    sizes = [(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), 
             (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create resized versions
    icon_sizes = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icon_sizes.append(resized)
    
    # Save as ICO
    icon_sizes[0].save(
        output_path,
        format='ICO',
        sizes=sizes,
        append_images=icon_sizes[1:]
    )
    
    print(f"✓ Created: {output_path}")
    print(f"  Sizes: {', '.join(f'{w}x{h}' for w, h in sizes)}")
    return output_path


def create_icns_file(png_path: Path, output_path: Path):
    """
    Create macOS .icns file.
    Note: This is a simplified version. For production, use 'iconutil' on macOS.
    """
    print(f"\n🍎 Creating ICNS file...")
    
    try:
        from PIL import Image
        import subprocess
        
        # Check if we're on macOS
        if sys.platform != 'darwin':
            print("⚠ ICNS creation works best on macOS with iconutil")
            print("  Creating simple .icns using PIL (may not work perfectly)")
        
        img = Image.open(png_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # macOS icon sizes
        sizes = [(16, 16), (32, 32), (64, 64), (128, 128), 
                 (256, 256), (512, 512), (1024, 1024)]
        
        icon_sizes = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_sizes.append(resized)
        
        # Save as ICNS (PIL support is limited)
        icon_sizes[0].save(
            output_path,
            format='ICNS',
            append_images=icon_sizes[1:]
        )
        
        print(f"✓ Created: {output_path}")
        print(f"  Sizes: {', '.join(f'{w}x{h}' for w, h in sizes)}")
        return output_path
        
    except Exception as e:
        print(f"✗ ICNS creation failed: {e}")
        print("  Install with: pip install pillow[icns]")
        return None


def create_sized_pngs(png_path: Path, output_dir: Path):
    """Create various PNG sizes for Linux and fallbacks."""
    print(f"\n🐧 Creating sized PNGs...")
    
    img = Image.open(png_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    sizes = {
        'icon_16.png': (16, 16),
        'icon_32.png': (32, 32),
        'icon_48.png': (48, 48),
        'icon_64.png': (64, 64),
        'icon_128.png': (128, 128),
        'icon_256.png': (256, 256),
    }
    
    created = []
    for name, size in sizes.items():
        out_path = output_dir / name
        resized = img.resize(size, Image.Resampling.LANCZOS)
        resized.save(out_path, 'PNG')
        created.append(f"{name} ({size[0]}x{size[1]})")
    
    print(f"✓ Created {len(created)} PNG files:")
    for item in created:
        print(f"  - {item}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_icon.py <input_png>")
        print("Example: python create_icon.py assets/icons/appicon.png")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"✗ File not found: {input_path}")
        sys.exit(1)
    
    if input_path.suffix.lower() != '.png':
        print(f"✗ Input must be a PNG file")
        sys.exit(1)
    
    print(f"🎨 Processing: {input_path}")
    
    # Check image size
    img = Image.open(input_path)
    print(f"   Original size: {img.width}x{img.height}")
    
    if img.width < 256 or img.height < 256:
        print("⚠ WARNING: Image should be at least 256x256 for best results")
        print("          Recommended: 512x512 or 1024x1024")
    
    output_dir = input_path.parent
    base_name = input_path.stem  # 'appicon' from 'appicon.png'
    
    # Create ICO for Windows
    ico_path = output_dir / f"{base_name}.ico"
    create_ico_file(input_path, ico_path)
    
    # Create ICNS for macOS
    icns_path = output_dir / f"{base_name}.icns"
    create_icns_file(input_path, icns_path)
    
    # Create sized PNGs
    create_sized_pngs(input_path, output_dir)
    
    print(f"\n✅ Done! Icon files created in: {output_dir}")
    print(f"\n📝 Next steps:")
    print(f"   1. Rebuild your app with PyInstaller")
    print(f"   2. Test the executable")
    print(f"   3. Taskbar icon should now appear!")


if __name__ == "__main__":
    main()