import os
from datetime import datetime
from py_svg2gcode import SVGConverter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
base_dir = os.getenv("COMMON_DIR")

def convert_svg_to_gcode(svg_file_path):
    """
    Convert an SVG file to G-code using SVGConverter class and save it in a directory.

    Args:
        svg_file_path (str): Path to the input SVG file.

    Returns:
        str: Path to the generated G-code file.
    """
    # Validate input file exists
    if not os.path.exists(svg_file_path):
        raise FileNotFoundError(f"SVG file not found: {svg_file_path}")
        
    # Create output directory if it doesn't exist
    output_dir = "gcode_experiments"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") #may use later, or may effect in frontend for database storage
    filename = os.path.splitext(os.path.basename(svg_file_path))[0]
    output_path = os.path.join(output_dir, f"{filename}.gcode")
    
    try:
        # Create converter instance and generate G-code
        converter = SVGConverter(debugging=True, toDefDir=False)
        gcode = converter.generate_gcode(svg_file_path)
        
        if not gcode:
            raise ValueError("Error: Generated G-code is empty")

        # Write G-code to file
        with open(output_path, 'w') as f:
            f.write(gcode)

        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Error converting SVG to G-code: {str(e)}")

if __name__ == "__main__":
    svg_file_path = f"{base_dir}/testing_images/signature.svg"
    
    try:
        output_file = convert_svg_to_gcode(svg_file_path)
        print(f"G-code generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
