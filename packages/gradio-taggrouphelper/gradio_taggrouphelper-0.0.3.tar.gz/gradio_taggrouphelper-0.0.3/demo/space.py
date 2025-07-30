
import gradio as gr
from app import demo as app
import os

_docs = {'TagGroupHelper': {'description': "A custom component that displays groups of clickable tags to help build prompts.\nWhen a tag is clicked, it's appended to a target Textbox component.\nThis component does not have a submittable value itself.", 'members': {'__init__': {'value': {'type': 'typing.Optional[typing.Dict[str, typing.List[str]]][\n    typing.Dict[str, typing.List[str]][\n        str, typing.List[str][str]\n    ],\n    None,\n]', 'default': 'None', 'description': 'A dictionary where keys are group names and values are lists of tags.'}, 'height': {'type': 'int | None', 'default': 'None', 'description': 'The height of the component container in pixels.'}, 'width': {'type': 'int | None', 'default': 'None', 'description': 'The width of the component container in pixels.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The label for this component, displayed above the groups.'}, 'font_size_scale': {'type': 'int', 'default': '100', 'description': 'A percentage to scale the font size of group headers and tags. Defaults to 100.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' seconds while the client connection is open."}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If False, the label is not displayed.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will not be wrapped in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'The relative size of the component compared to others in a `gr.Row` or `gr.Column`.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'The minimum width of the component in pixels.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an selectable component; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'target_textbox_id': {'type': 'str | None', 'default': 'None', 'description': 'The `elem_id` of the `gr.Textbox` component to target. Required.'}, 'separator': {'type': 'str', 'default': '", "', 'description': 'The string to use as a separator between tags. Defaults to ", ". Can be set to " " for space separation.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings to assign as CSS classes to the component.'}}, 'postprocess': {'value': {'type': 'typing.Optional[typing.Dict[str, typing.List[str]]][\n    typing.Dict[str, typing.List[str]][\n        str, typing.List[str][str]\n    ],\n    None,\n]', 'description': None}}, 'preprocess': {'return': {'type': 'Any', 'description': None}, 'value': None}}, 'events': {}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'TagGroupHelper': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_taggrouphelper`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_taggrouphelper/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_taggrouphelper"></a>  
</div>

A fast text generator based on tagged words
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_taggrouphelper
```

## Usage

```python
#
# demo/app.py
#
import gradio as gr
from gradio_taggrouphelper import TagGroupHelper 

# Example data structure for the tags and groups
TAG_DATA = {
    "Quality": [
        "best quality", "masterpiece", "high resolution", "4k", "8k", 
        "sharp focus", "detailed", "photorealistic"
    ],
    "Lighting": [
        "cinematic lighting", "volumetric lighting", "god rays", 
        "golden hour", "studio lighting", "dramatic lighting"
    ],
    "Style": [
        "anime style", "oil painting", "concept art", "fantasy", 
        "steampunk", "vaporwave", "line art"
    ],
    "Negative Prompts": [
        "blurry", "noisy", "low resolution", "low quality", "watermark",
        "text", "bad anatomy", "extra limbs", "disfigured"
    ]
}

css=\"\"\" 
body {    
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;    
    margin: 0;
    padding: 0;
}
.gradio-container {    
    border-radius: 15px;
    padding: 30px 40px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    margin: 40px 340px;    
}
.gradio-container h1 {    
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}
.fillable {
    width: 100% !important;
    max-width: unset !important;
}
#examples_container {
    margin: auto;
    width: 90%;
}
#examples_row {
    justify-content: center;
}
#tips_row{    
    padding-left: 20px;
}
.sidebar {    
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.sidebar .toggle-button {    
    background: linear-gradient(90deg, #34d399, #10b981) !important;
    border: none;    
    padding: 12px 18px;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 1px;
    border-radius: 5px;
    cursor: pointer;
    transition: transform 0.2s ease-in-out;
}
.toggle-button:hover {
    transform: scale(1.05);
}
.sidebar .sidebar-content {
    padding-left: 10px !important;
}
.sidebar .sidebar-content .column .block div .prose {
    text-align: center;
}
\"\"\"
with gr.Blocks(theme=gr.themes.Ocean(), css=css) as demo:
    gr.Markdown("# Tag Group Helper Demo")
    gr.Markdown("Click on the tags below to add them to the prompt textboxes.")
    gr.Markdown("<span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_taggrouphelper'>GitHub Code</a></span>")
    with gr.Row():
        with gr.Column(scale=2): # Give more space to the textboxes
            # Create the target Textbox and give it a unique `elem_id`.
            positive_prompt_box = gr.Textbox(
                label="Positive Prompt",
                placeholder="Click tags from 'Prompt Keywords' to add them here...",
                lines=5,
                elem_id="positive-prompt-textbox" # This ID must be unique
            )
            negative_prompt_box = gr.Textbox(
                label="Negative Prompt",
                placeholder="Click tags from 'Negative Keywords' to add them here...",
                lines=5,
                elem_id="negative-prompt-textbox" # This ID must be unique
            )
        with gr.Sidebar(position="right"):           
            # Create an instance of the TagGroupHelper for the Positive Prompt box.
            TagGroupHelper(
                label="Positive Prompt Keywords",
                value={k: v for k, v in TAG_DATA.items() if "Negative" not in k},
                target_textbox_id="positive-prompt-textbox",
                separator=", ",
                interactive=True,
                width=250,
                font_size_scale=90
                
            )
            
            # Create another instance for the Negative Prompt box.
            TagGroupHelper(
                label="Negative Prompt Keywords",
                value={"Negative Prompts": TAG_DATA["Negative Prompts"]},
                target_textbox_id="negative-prompt-textbox",
                separator=", ",
                interactive=True,
                width=250,                
                font_size_scale=90
            )

if __name__ == '__main__':
    demo.launch()
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `TagGroupHelper`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["TagGroupHelper"]["members"]["__init__"], linkify=[])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.



 ```python
def predict(
    value: Any
) -> typing.Optional[typing.Dict[str, typing.List[str]]][
    typing.Dict[str, typing.List[str]][
        str, typing.List[str][str]
    ],
    None,
]:
    return value
```
""", elem_classes=["md-custom", "TagGroupHelper-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          TagGroupHelper: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
