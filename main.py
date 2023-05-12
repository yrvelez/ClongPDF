from flask import Flask, request, render_template, jsonify
import pdfplumber
import os
import anthropic

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def upload_form():
  if request.method == 'POST':
    file = request.files.get('file')
    prompt = request.form.get('prompt')
    tokens = request.form.get('tokens')

    temp_file = "/tmp/temp.pdf"
    file.save(temp_file)

    pdf_text = ""
    with pdfplumber.open(temp_file) as pdf:
      for page in pdf.pages:
        pdf_text += page.extract_text()

    print(f"PDF Text: {pdf_text}")  # Debug line

    c = anthropic.Client(os.environ['claude'])

    resp = c.completion(
      prompt=f"{anthropic.HUMAN_PROMPT}{pdf_text}{prompt}{anthropic.AI_PROMPT}",
      stop_sequences=[anthropic.HUMAN_PROMPT],
      model="claude-v1-100k",
      max_tokens_to_sample= tokens,
    )
    output = resp.get('completion')

    print(f"API Response: {output}")  # Debug line

    os.remove(temp_file)  # delete the temporary file

    return render_template("output.html", output=output)

  return render_template('upload.html')


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
