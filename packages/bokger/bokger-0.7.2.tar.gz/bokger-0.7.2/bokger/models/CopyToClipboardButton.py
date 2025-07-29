from bokeh.models import CustomJS
from bokeh.models.widgets import Button
import os

_js_path = os.path.join(os.path.dirname(__file__),"CopyToClipboard.js")
_js_code = open(_js_path).read()

def copyToClipboardButton(txt : str)-> Button:
    button_label = f"copy to clipboard"
    button = Button(label=button_label, button_type="success")
    _js = CustomJS(args=dict(txt=txt),code=_js_code)
    button.js_on_click(_js)
    return button

if __name__ =='__main__':
    from bokeh.io import show
    from bokeh.plotting import output_file
    output_file(filename = "save_txt.html", mode='inline')
    
    button = copyToClipboardButton("hello world","example txt")

    show(button)
