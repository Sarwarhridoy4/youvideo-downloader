"""
create_icon.py - Professional Multi-Platform Icon Generator
------------------------------------------------------------
Creates optimized icon files for Windows, macOS, and Linux from a single PNG.

Features:
• Windows ICO with all required sizes (16-256px)
• macOS ICNS with Retina support (16-1024px)
• Linux PNG icons in standard sizes
• Proper transparency and optimization
• Validates input and provides guidance

Usage:
    python create_icon.py assets/icons/appicon.png
"""

import sys
import os
from pathlib import Path
from PIL import Image
import subprocess


def validate_input(png_path: Path) -> bool:
    """Validate input PNG file"""
    if not png_path.exists():
        print(f"❌ File not found: {png_path}")
        return False
    
    if png_path.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
        print(f"❌ Input must be PNG or JPEG (will be converted to PNG)")
        return False
    
    try:
        img = Image.open(png_path)
        print(f"📐 Image size: {img.width}x{img.height}")
        print(f"📊 Image mode: {img.mode}")
        
        if img.width < 256 or img.height < 256:
            print(f"\n⚠️  WARNING: Image is smaller than recommended!")
            print(f"   Current: {img.width}x{img.height}")
            print(f"   Recommended: 512x512 or 1024x1024")
            print(f"   Minimum: 256x256")
            
            response = input("\n   Continue anyway? (y/n): ").lower()
            if response != 'y':
                return False
        
        if img.width != img.height:
            print(f"\n⚠️  WARNING: Image is not square!")
            print(f"   Current: {img.width}x{img.height}")
            print(f"   Icons should be square for best results")
            
            response = input("\n   Continue anyway? (y/n): ").lower()
            if response != 'y':
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading image: {e}")
        return False


def prepare_image(png_path: Path) -> Image.Image:
    """Load and prepare image with proper format"""
    print(f"\n🎨 Preparing image...")
    
    img = Image.open(png_path)
    
    # Convert to RGBA for transparency
    if img.mode != 'RGBA':
        print(f"   Converting {img.mode} → RGBA")
        img = img.convert('RGBA')
    
    # Make square if needed
    if img.width != img.height:
        size = max(img.width, img.height)
        print(f"   Making square: {size}x{size}")
        
        square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        offset_x = (size - img.width) // 2
        offset_y = (size - img.height) // 2
        square.paste(img, (offset_x, offset_y))
        img = square
    
    print(f"✓ Image prepared: {img.width}x{img.height} RGBA")
    return img


def create_ico_file(img: Image.Image, output_path: Path) -> bool:
    """
    Create optimized Windows .ico file with all standard sizes.
    Includes sizes needed for taskbar, system tray, and file explorer.
    """
    print(f"\n🪟 Creating Windows ICO file...")
    
    try:
        # Windows standard icon sizes (including high-DPI variants)
        sizes = [
            (16, 16),   # Small icons, system tray
            (20, 20),   # 125% DPI
            (24, 24),   # 150% DPI
            (32, 32),   # Medium icons, taskbar
            (40, 40),   # 125% DPI taskbar
            (48, 48),   # Large icons, file explorer
            (64, 64),   # Extra large
            (96, 96),   # 200% DPI
            (128, 128), # Jumbo icons
            (256, 256), # Maximum ICO size
        ]
        
        # Create resized versions
        print(f"   Generating {len(sizes)} sizes...")
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICO with all sizes embedded
        icon_images[0].save(
            output_path,
            format='ICO',
            sizes=sizes,
            append_images=icon_images[1:]
        )
        
        file_size = output_path.stat().st_size / 1024
        print(f"✅ Created: {output_path}")
        print(f"   File size: {file_size:.1f} KB")
        print(f"   Sizes: {', '.join(f'{w}x{h}' for w, h in sizes)}")
        return True
        
    except Exception as e:
        print(f"❌ ICO creation failed: {e}")
        return False


def create_icns_file_native(img: Image.Image, output_path: Path) -> bool:
    """
    Create macOS .icns using native iconutil (macOS only).
    This produces the highest quality ICNS files.
    """
    if sys.platform != 'darwin':
        return False
    
    if not subprocess.run(['which', 'iconutil'], capture_output=True).returncode == 0:
        return False
    
    print(f"\n🍎 Creating macOS ICNS (native iconutil)...")
    
    try:
        import tempfile
        import shutil
        
        # Create temporary iconset directory
        with tempfile.TemporaryDirectory() as tmpdir:
            iconset_path = Path(tmpdir) / "icon.iconset"
            iconset_path.mkdir()
            
            # macOS icon sizes with @2x variants
            sizes = [
                ('icon_16x16.png', 16),
                ('icon_16x16@2x.png', 32),
                ('icon_32x32.png', 32),
                ('icon_32x32@2x.png', 64),
                ('icon_128x128.png', 128),
                ('icon_128x128@2x.png', 256),
                ('icon_256x256.png', 256),
                ('icon_256x256@2x.png', 512),
                ('icon_512x512.png', 512),
                ('icon_512x512@2x.png', 1024),
            ]
            
            print(f"   Generating {len(sizes)} sizes for iconset...")
            for filename, size in sizes:
                icon_file = iconset_path / filename
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(icon_file, 'PNG')
            
            # Use iconutil to create ICNS
            result = subprocess.run(
                ['iconutil', '-c', 'icns', str(iconset_path), '-o', str(output_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                file_size = output_path.stat().st_size / 1024
                print(f"✅ Created: {output_path}")
                print(f"   File size: {file_size:.1f} KB")
                print(f"   Method: iconutil (native)")
                return True
            else:
                print(f"❌ iconutil failed: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Native ICNS creation failed: {e}")
        return False


def create_icns_file_pillow(img: Image.Image, output_path: Path) -> bool:
    """
    Create macOS .icns using Pillow (cross-platform fallback).
    Works on any OS but may not be as optimized as native iconutil.
    """
    print(f"\n🍎 Creating macOS ICNS (Pillow)...")
    
    try:
        # macOS standard sizes including Retina
        sizes = [
            (16, 16), (32, 32), (64, 64), (128, 128),
            (256, 256), (512, 512), (1024, 1024)
        ]
        
        print(f"   Generating {len(sizes)} sizes...")
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        # Save as ICNS
        icon_images[0].save(
            output_path,
            format='ICNS',
            append_images=icon_images[1:]
        )
        
        file_size = output_path.stat().st_size / 1024
        print(f"✅ Created: {output_path}")
        print(f"   File size: {file_size:.1f} KB")
        print(f"   Method: Pillow (cross-platform)")
        return True
        
    except Exception as e:
        print(f"❌ Pillow ICNS creation failed: {e}")
        print(f"💡 Try: pip install pillow[icns]")
        return False


def create_icns_file(img: Image.Image, output_path: Path) -> bool:
    """Create macOS ICNS using best available method"""
    # Try native iconutil first (best quality)
    if create_icns_file_native(img, output_path):
        return True
    
    # Fallback to Pillow
    return create_icns_file_pillow(img, output_path)


def create_linux_icons(img: Image.Image, output_dir: Path) -> bool:
    """
    Create standard Linux icon sizes (PNG format).
    These follow freedesktop.org icon theme specifications.
    """
    print(f"\n🐧 Creating Linux PNG icons...")
    
    try:
        # Standard Linux icon sizes
        sizes = {
            'icon_16.png': 16,
            'icon_22.png': 22,   # GNOME panel
            'icon_24.png': 24,   # GNOME panel
            'icon_32.png': 32,
            'icon_48.png': 48,
            'icon_64.png': 64,
            'icon_128.png': 128,
            'icon_256.png': 256,
            'icon_512.png': 512, # High-DPI displays
        }
        
        print(f"   Generating {len(sizes)} standard sizes...")
        created = []
        
        for filename, size in sizes.items():
            out_path = output_dir / filename
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(out_path, 'PNG', optimize=True)
            
            file_size = out_path.stat().st_size / 1024
            created.append(f"{filename} ({size}x{size}, {file_size:.1f}KB)")
        
        print(f"✅ Created {len(created)} PNG files:")
        for item in created:
            print(f"   • {item}")
        
        return True
        
    except Exception as e:
        print(f"❌ PNG creation failed: {e}")
        return False


def create_favicon(img: Image.Image, output_path: Path) -> bool:
    """Create favicon.ico for web use (optional)"""
    print(f"\n🌐 Creating favicon.ico...")
    
    try:
        sizes = [(16, 16), (32, 32), (48, 48)]
        
        icon_images = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icon_images.append(resized)
        
        icon_images[0].save(
            output_path,
            format='ICO',
            sizes=sizes,
            append_images=icon_images[1:]
        )
        
        file_size = output_path.stat().st_size / 1024
        print(f"✅ Created: {output_path} ({file_size:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"⚠️  Favicon creation failed: {e}")
        return False


def main():
    print("=" * 70)
    print("🎨 Multi-Platform Icon Generator")
    print("=" * 70)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("\n❌ Usage: python create_icon.py <input_png>")
        print("\nExamples:")
        print("   python create_icon.py assets/icons/appicon.png")
        print("   python create_icon.py myicon.png")
        print("\n💡 Recommended input: Square PNG, 512x512 or larger")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    # Validate input
    print(f"\n📂 Input: {input_path}")
    if not validate_input(input_path):
        sys.exit(1)
    
    # Prepare image
    img = prepare_image(input_path)
    
    # Determine output directory and base name
    output_dir = input_path.parent
    base_name = input_path.stem
    
    print(f"\n📁 Output directory: {output_dir}")
    print(f"🏷️  Base name: {base_name}")
    
    # Track success
    results = {
        'ico': False,
        'icns': False,
        'png': False,
        'favicon': False
    }
    
    # Create Windows ICO
    ico_path = output_dir / f"{base_name}.ico"
    results['ico'] = create_ico_file(img, ico_path)
    
    # Create macOS ICNS
    icns_path = output_dir / f"{base_name}.icns"
    results['icns'] = create_icns_file(img, icns_path)
    
    # Create Linux PNGs
    results['png'] = create_linux_icons(img, output_dir)
    
    # Create favicon (optional, for web)
    if base_name == 'appicon':
        favicon_path = output_dir / "favicon.ico"
        results['favicon'] = create_favicon(img, favicon_path)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n✅ Success: {success_count}/{total_count}")
    print(f"\n   Windows ICO:  {'✅' if results['ico'] else '❌'}")
    print(f"   macOS ICNS:   {'✅' if results['icns'] else '❌'}")
    print(f"   Linux PNGs:   {'✅' if results['png'] else '❌'}")
    if results['favicon']:
        print(f"   Favicon:      ✅")
    
    if success_count == total_count:
        print("\n🎉 All icons created successfully!")
    elif success_count > 0:
        print("\n⚠️  Some icons created, but with warnings")
    else:
        print("\n❌ Icon creation failed")
        sys.exit(1)
    
    # Next steps
    print("\n" + "=" * 70)
    print("📝 NEXT STEPS")
    print("=" * 70)
    print("\n1. Verify icon quality:")
    print(f"   • Open {ico_path} on Windows")
    print(f"   • Open {icns_path} on macOS")
    print(f"   • Check PNG files on Linux")
    
    print("\n2. Update your application:")
    print("   • Windows: Use .ico in PyInstaller spec")
    print("   • macOS: Use .icns in PyInstaller spec")
    print("   • Linux: Use .png files")
    
    print("\n3. Rebuild executable:")
    print("   pyinstaller yourvideo-downloader.spec")
    
    print("\n4. Test taskbar icon:")
    print("   • Run the rebuilt executable")
    print("   • Check taskbar/dock/launcher")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)