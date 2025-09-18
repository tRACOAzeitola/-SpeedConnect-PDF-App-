#!/usr/bin/env python3
"""
Create a company logo icon for SpeedConnect PDF Merger
"""

import os
from pathlib import Path

def create_icon():
    """Create a company logo icon."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create assets directory
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        
        # Icon specifications
        size = (256, 256)
        background_color = '#1E1E1E'  # Dark background
        primary_color = '#FF3B30'     # SpeedConnect red
        secondary_color = '#007AFF'   # SpeedConnect blue
        text_color = '#FFFFFF'        # White text
        
        # Create image
        img = Image.new('RGBA', size, background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw background circle
        margin = 20
        draw.ellipse([margin, margin, size[0]-margin, size[1]-margin], 
                    fill=primary_color, outline=secondary_color, width=4)
        
        # Draw connection lines (representing "Speed" and "Connect")
        center = size[0] // 2
        # Horizontal lines
        draw.rectangle([60, center-15, 196, center-10], fill=text_color)
        draw.rectangle([60, center+10, 196, center+15], fill=text_color)
        
        # Connection dots
        dot_size = 12
        draw.ellipse([50-dot_size//2, center-dot_size//2, 50+dot_size//2, center+dot_size//2], fill=secondary_color)
        draw.ellipse([206-dot_size//2, center-dot_size//2, 206+dot_size//2, center+dot_size//2], fill=secondary_color)
        
        # Add PDF text
        try:
            font_large = ImageFont.truetype("Arial Bold", 28)
            font_small = ImageFont.truetype("Arial", 16)
        except:
            try:
                font_large = ImageFont.truetype("Arial", 28)
                font_small = ImageFont.truetype("Arial", 16)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # Main text
        draw.text((center, 80), "SC", fill=text_color, font=font_large, anchor='mm')
        draw.text((center, 180), "PDF", fill=text_color, font=font_small, anchor='mm')
        
        # Save as ICO (Windows)
        ico_path = assets_dir / "icon.ico"
        img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"✅ Ícone Windows criado: {ico_path}")
        
        # Save as PNG (universal)
        png_path = assets_dir / "icon.png"
        img.save(png_path, format='PNG')
        print(f"✅ Ícone PNG criado: {png_path}")
        
        # Create ICNS for macOS
        try:
            icns_path = assets_dir / "icon.icns"
            # Create different sizes for ICNS
            sizes_icns = [16, 32, 64, 128, 256, 512]
            images = []
            
            for s in sizes_icns:
                resized = img.resize((s, s), Image.Resampling.LANCZOS)
                images.append(resized)
            
            # Save as ICNS (this might not work on all systems)
            try:
                img.save(icns_path, format='ICNS', sizes=[(s, s) for s in sizes_icns])
                print(f"✅ Ícone macOS criado: {icns_path}")
            except:
                print("⚠️ Não foi possível criar .icns, usando .png como alternativa")
        except:
            pass
        
        return True
        
    except ImportError:
        print("❌ Pillow não está instalado. Execute: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Erro ao criar ícone: {e}")
        return False

def main():
    """Main function."""
    print("🎨 Criando ícone da SpeedConnect...")
    
    if create_icon():
        print("\n🎉 Ícones criados com sucesso!")
        print("Os ícones estão na pasta 'assets/'")
    else:
        print("\n❌ Falha ao criar ícones")

if __name__ == "__main__":
    main()
