import gradio as gr
from script import ui

with gr.Blocks() as demo:
    ui()

demo.launch()
