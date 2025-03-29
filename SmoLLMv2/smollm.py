import gradio as gr
import requests
import json

def query_ollama(prompt):
    url = 'http://10.17.10.204:11434/api/generate'
    data = {
        'model': 'smollm2:135m',
        'prompt': prompt
    }

    try:
        with requests.post(url, json=data, stream=True) as response:
            response.raise_for_status()
            result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode('utf-8')
                        data = json.loads(chunk)
                        result += data.get('response', '')
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError as e:
                        return f"Error parsing response: {e}\nRaw data: {chunk}"
            return result.strip()
    except Exception as e:
        return str(e)

def chat_interface(prompt):
    return query_ollama(prompt)

demo = gr.Blocks(theme=gr.themes.Base(primary_hue="blue", secondary_hue="gray"))

with demo:
    gr.HTML('<img src="https://timnetworks.net/img/smollm.png" alt="SmoLLM" style="display:block;margin:16px auto;width:150px;" />')
    gr.Markdown("Chat with a locally hosted edge model: smollm2:135m.")
    prompt = gr.Textbox(label="Enter your prompt:", lines=3, placeholder="Type your question here...")
    output = gr.Textbox(label="Response:", lines=10)
    btn = gr.Button("Submit")

    def on_click(prompt_text):
        return query_ollama(prompt_text)

    btn.click(on_click, inputs=[prompt], outputs=[output])

demo.launch(favicon_path="./logo.png", server_name="0.0.0.0", server_port=7861)

