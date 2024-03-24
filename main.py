from PIL import Image
from flask import Flask, request, jsonify, render_template_string
import base64
from io import BytesIO
from dotenv import load_dotenv

from openai import OpenAI



app = Flask(__name__)


load_dotenv()


client = OpenAI(api_key="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")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image1' not in request.files or 'image2' not in request.files:
            return "Missing images", 400
        file1 = request.files['image1']
        file2 = request.files['image2']

        if file1.filename == '' or file2.filename == '':
            return "No selected file", 400

        if file1 and file2:
            base64_image1 = encode_image_to_base64(file1)
            base64_image2 = encode_image_to_base64(file2)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I need to verify if the person in the photo is wearing the same t-shirt. Give me the response with the similarity score with SIMILAR: {score} range from 0 - 10",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image1}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image2}"
                            }
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        content = response.choices[0].message.content
        similar_scoāre = content.split('SIMILAR:')[-1].strip()
        total_tokens_used = response.usage.total_tokens

        result = f"Similarity Score: {similar_score}, Total Tokens Used: {total_tokens_used}"
        return render_template_string(HTML_TEMPLATE, result=result)
    else:
        return render_template_string(HTML_TEMPLATE, result=None)


def encode_image_to_base64(image_file):
    """Encode an image file to a base64 string."""
    buffered = BytesIO()
    img = Image.open(image_file)
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Verify T-Shirts</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
            padding-top: 50px;
        }
        h2 {
            color: #333;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            display: inline-block;
            margin: auto;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        input[type=file] {
            margin-bottom: 20px;
        }
        input[type=submit] {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type=submit]:hover {
            background-color: #0056b3;
        }
        .result {
            margin-top: 20px;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            display: inline-block;
            margin: auto;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h2>Verify T-Shirts</h2>
    <form method="post" enctype="multipart/form-data">
        <label for="image1">Update Company's T-Shirt Photo:</label><br>
        <input type="file" name="image1" id="image1" required><br>
        <label for="image2">Upload Your Photo for Verification:</label><br>
        <input type="file" name="image2" id="image2" required><br><br>
        <input type="submit" value="Compare">
    </form>
    {% if result %}
        <div class="result">
            <h3>Result:</h3>
            <p>{{ result }}</p>
        </div>
    {% endif %}
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)
