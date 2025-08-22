import cv2
import numpy as np
import json

# Load components from JSON file
def load_components_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            components_data = json.load(file)
            print(components_data)
        return components_data["components"]
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file_path}'.")
        return []

# Load a blank image or your background diagram
image = cv2.imread("images/4.png")  # replace with your image file
if image is None:
    # if you don’t have a background, create a white canvas
    image = 255 * np.ones((300, 400, 3), dtype=np.uint8)

# Load components from JSON file
components = load_components_from_json("components_relations.json")

# Predefined distinct colors (BGR format for OpenCV)
colors = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Lime Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta / Fuchsia
    (0, 255, 255),    # Cyan / Aqua
    (255, 128, 0),    # Orange
    (128, 0, 128),    # Purple
    (128, 128, 128),  # Gray
    (255, 165, 0),    # Dark Orange (more classic)
    (0, 128, 0),      # Green (Forest)
    (0, 0, 128),      # Navy Blue
    (128, 0, 0),      # Maroon
    (255, 192, 203),  # Pink
    (165, 42, 42),    # Brown
    (0, 255, 127),    # Spring Green
    (70, 130, 180),   # Steel Blue
    (255, 215, 0),    # Gold
    (106, 90, 205),   # Slate Blue
    (255, 20, 147),   # Deep Pink
    (32, 178, 170),    # Light Sea Green
    (35, 178, 175),    # Light Sea Green
    (32, 178, 160)    # Light Sea Green
]

# Draw each component
for i, comp in enumerate(components):
    x, y = comp["position"]["x"], comp["position"]["y"]
    color = colors[i % len(colors)]  # cycle colors if more components

    # draw circle
    cv2.circle(image, (x, y), 6, color, -1)

    # draw label with same color
    cv2.putText(image, comp["name"], (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

# Show result
cv2.imshow("Colored Components", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save result
cv2.imwrite("diagram_colored_components.png", image)
