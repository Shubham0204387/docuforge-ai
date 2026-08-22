"""Render PlantUML diagrams to PNG and SVG"""
import subprocess
import tempfile
import os
import base64
from typing import Optional

class PlantUMLRenderer:
    """Convert PlantUML code to images using local plantuml command"""
    
    @staticmethod
    def render_to_png(plantuml_code: str) -> Optional[bytes]:
        """
        Render PlantUML to PNG and return bytes
        Returns PNG bytes or None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(plantuml_code)
                temp_file = f.name
            
            # Run plantuml command
            result = subprocess.run(
                ['plantuml', '-tpng', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            png_file = temp_file.replace('.puml', '.png')
            if os.path.exists(png_file):
                with open(png_file, 'rb') as img:
                    png_bytes = img.read()
                os.unlink(png_file)
                os.unlink(temp_file)
                return png_bytes
        except Exception as e:
            print(f"PlantUML render error: {e}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        return None
    
    @staticmethod
    def render_to_svg(plantuml_code: str) -> Optional[str]:
        """
        Render PlantUML to SVG and return as string
        Returns SVG string or None
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
                f.write(plantuml_code)
                temp_file = f.name
            
            result = subprocess.run(
                ['plantuml', '-tsvg', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            svg_file = temp_file.replace('.puml', '.svg')
            if os.path.exists(svg_file):
                with open(svg_file, 'r') as img:
                    svg_text = img.read()
                os.unlink(svg_file)
                os.unlink(temp_file)
                return svg_text
        except Exception as e:
            print(f"PlantUML SVG render error: {e}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        return None
    
    @staticmethod
    def render_to_base64_png(plantuml_code: str) -> Optional[str]:
        """Render to PNG and return base64 encoded string"""
        png_bytes = PlantUMLRenderer.render_to_png(plantuml_code)
        if png_bytes:
            return base64.b64encode(png_bytes).decode('utf-8')
        return None
