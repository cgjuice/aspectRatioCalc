#aspectRatioCalc v05
# Copyright (c) 2024 Giuseppe Pagnozzi
#
# This script is provided freely and generously.
# You can use, study, modify, and share it.
# It's licensed under the MIT License
# visit https://opensource.org/licenses/MIT for the full terms.


import maya.cmds as cmds
import math

def calculate_aspect_ratio(width, height):
    """Calculates aspect ratio in decimal and simplified ratio format."""
    if height == 0:
        return "N/A", "N/A"
    decimal_ratio = width / float(height)

    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    common_divisor = gcd(int(width), int(height))
    simplified_width = int(width) // common_divisor
    simplified_height = int(height) // common_divisor
    ratio_string = f"{simplified_width}:{simplified_height}"

    return decimal_ratio, ratio_string

def calculate_height_from_ratio(width, ratio_text):
    """Calculates height from width and aspect ratio (text input)."""
    try:
        if not ratio_text.strip(): 
            return "Invalid Ratio"
        if ":" in ratio_text:
            ratio_parts = ratio_text.split(":")
            if len(ratio_parts) != 2 or not ratio_parts[0].strip() or not ratio_parts[1].strip():
                return "Invalid Ratio"
            ratio = float(ratio_parts[0]) / float(ratio_parts[1])
        else:
            ratio = float(ratio_text)
        if ratio == 0:
            return "N/A"
        height = width / ratio
        return height
    except ValueError:
        return "Invalid Ratio"
    except ZeroDivisionError: 
        return "Invalid Ratio (div by zero)"


def calculate_width_from_ratio(height, ratio_text):
    """Calculates width from height and aspect ratio (text input)."""
    try:
        if not ratio_text.strip(): 
            return "Invalid Ratio"
        if ":" in ratio_text:
            ratio_parts = ratio_text.split(":")
            if len(ratio_parts) != 2 or not ratio_parts[0].strip() or not ratio_parts[1].strip():
                return "Invalid Ratio"
            ratio = float(ratio_parts[0]) / float(ratio_parts[1])
        else:
            ratio = float(ratio_text)
        width = height * ratio
        return width
    except ValueError:
        return "Invalid Ratio"
    except ZeroDivisionError: 
        return "Invalid Ratio (div by zero)"


def aspect_ratio_calculator_ui():
    if cmds.window("aspectRatioWin", exists=True):
        cmds.deleteUI("aspectRatioWin")

    cmds.window("aspectRatioWin", title="Aspect Ratio Calculator", widthHeight=(300, 350))
    cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 5))

    cmds.text(label="Pixel Dimensions and Aspect Ratio Calculator", align="center", font="boldLabelFont")
    cmds.separator(style='single')

    field_column_widths = [200, 80]
    width_field = cmds.intFieldGrp(numberOfFields=1, label='Width (pixels):', value1=1920, columnWidth2=field_column_widths)
    height_field = cmds.intFieldGrp(numberOfFields=1, label='Height (pixels):', value1=1080, columnWidth2=field_column_widths)
    ratio_field = cmds.textFieldGrp(label='Aspect Ratio (e.g., 16:9 or 2.5):', text="16:9", columnWidth2=field_column_widths)

    aspect_ratio_decimal_text = cmds.text(label="Decimal Ratio: ", align="left")
    aspect_ratio_ratio_text = cmds.text(label="Ratio (Simplified): ", align="left")

    def calculate_aspect_command(*args):
        width = cmds.intFieldGrp(width_field, query=True, value1=True)
        height = cmds.intFieldGrp(height_field, query=True, value1=True)
        decimal_ratio, ratio_string = calculate_aspect_ratio(width, height)
        cmds.text(aspect_ratio_decimal_text, edit=True, label=f"Decimal Ratio: {decimal_ratio}")
        cmds.text(aspect_ratio_ratio_text, edit=True, label=f"Ratio (Simplified): {ratio_string}")
        if ratio_string != "N/A":
            cmds.textFieldGrp(ratio_field, edit=True, text=ratio_string)
        elif decimal_ratio == "N/A": 
             cmds.textFieldGrp(ratio_field, edit=True, text="") 

    def calculate_height_command(*args):
        width = cmds.intFieldGrp(width_field, query=True, value1=True)
        ratio_text_val = cmds.textFieldGrp(ratio_field, query=True, text=True)
        calculated_height = calculate_height_from_ratio(width, ratio_text_val)

        if isinstance(calculated_height, (int, float)):
            cmds.intFieldGrp(height_field, edit=True, value1=int(round(calculated_height)))
            calculate_aspect_command()
        else: 
            cmds.intFieldGrp(height_field, edit=True, value1=0)
            cmds.text(aspect_ratio_decimal_text, edit=True, label=f"Decimal Ratio: {calculated_height}")
            cmds.text(aspect_ratio_ratio_text, edit=True, label="Ratio (Simplified): N/A")


    def calculate_width_command(*args):
        height = cmds.intFieldGrp(height_field, query=True, value1=True)
        ratio_text_val = cmds.textFieldGrp(ratio_field, query=True, text=True)
        calculated_width = calculate_width_from_ratio(height, ratio_text_val)

        if isinstance(calculated_width, (int, float)):
            cmds.intFieldGrp(width_field, edit=True, value1=int(round(calculated_width)))
            calculate_aspect_command()
        else: 
            cmds.intFieldGrp(width_field, edit=True, value1=0)
            cmds.text(aspect_ratio_decimal_text, edit=True, label=f"Decimal Ratio: {calculated_width}")
            cmds.text(aspect_ratio_ratio_text, edit=True, label="Ratio (Simplified): N/A")


    def apply_resolution_command(*args):
        width = cmds.intFieldGrp(width_field, query=True, value1=True)
        height = cmds.intFieldGrp(height_field, query=True, value1=True)

        if height == 0:
            cmds.warning("Cannot apply resolution with height 0.")
            return

        cmds.setAttr("defaultResolution.pixelAspect", 1.0)
        cmds.setAttr("defaultResolution.width", width)
        cmds.setAttr("defaultResolution.height", height)

        dar = float(width) / float(height) * 1.0
        cmds.setAttr("defaultResolution.deviceAspectRatio", dar)

        print(f"Resolution set to {width}x{height} (Pixel Aspect Ratio: 1.0)")

    def apply_ratio_to_camera_command(*args):
        selected_objects = cmds.ls(selection=True)

        if not selected_objects:
            cmds.warning("No camera selected. Please select a camera (transform or shape).")
            return

        camera_shape_nodes = []

        for obj in selected_objects:
            if cmds.nodeType(obj) == 'camera':
                camera_shape_nodes.append(obj)
            elif cmds.nodeType(obj) == 'transform':
                shapes = cmds.listRelatives(obj, shapes=True, type='camera')
                if shapes:
                    camera_shape_nodes.extend(shapes)

        if not camera_shape_nodes:
            cmds.warning("No camera shape nodes found in selection. Please select a camera transform or shape.")
            return

        camera_shape_name = camera_shape_nodes[0]

        try:
            decimal_ratio_text = cmds.text(aspect_ratio_decimal_text, query=True, label=True)
            if ": " not in decimal_ratio_text:
                cmds.warning("Decimal Ratio not calculated or invalid. Calculate aspect ratio first.")
                return

            decimal_ratio_str = decimal_ratio_text.split(": ")[1]
            if decimal_ratio_str == "N/A": 
                cmds.warning("Aspect Ratio is N/A. Calculate aspect ratio first.")
                return
            decimal_ratio = float(decimal_ratio_str)


            vertical_aperture = cmds.getAttr(camera_shape_name + ".verticalFilmAperture")
            new_horizontal_aperture = vertical_aperture * decimal_ratio

            cmds.setAttr(camera_shape_name + ".horizontalFilmAperture", new_horizontal_aperture)
            print(f"Applied Film Aspect Ratio ({decimal_ratio:.2f}) to camera '{cmds.listTransforms(camera_shape_name)[0]}'.")

        except ValueError:
            cmds.warning("Invalid Aspect Ratio. Please calculate a valid aspect ratio.")
        except IndexError: 
            cmds.warning("Could not parse Decimal Ratio. Calculate aspect ratio first.")
        except Exception as e:
            cmds.warning(f"Error applying ratio to camera: {e}")


    cmds.text(label="\nStep 1: Enter Width, Height, or Aspect Ratio above.\nStep 2: Calculate the missing value below.", align="left", height=60)
    cmds.button(label="Calculate Width from Ratio", command=calculate_width_command)
    cmds.button(label="Calculate Height from Ratio", command=calculate_height_command)
    cmds.button(label="Calculate Aspect Ratio", command=calculate_aspect_command) 
    cmds.text(label="\nStep 3: Apply the settings.", align="left", height=40)
    cmds.button(label="Apply Resolution to Scene", command=apply_resolution_command)
    cmds.button(label="Apply Film Aspect Ratio to the selected Camera", command=apply_ratio_to_camera_command)
    cmds.showWindow("aspectRatioWin")

aspect_ratio_calculator_ui()