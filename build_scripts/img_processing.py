import base64

img_path = "./res/trolley-problem.png"

# Read the image and convert to base64
with open(img_path, "rb") as image_file:
    base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")

# Display the encoded string
print(f"![Alt Text](data:image/png;base64,{base64_encoded})")
