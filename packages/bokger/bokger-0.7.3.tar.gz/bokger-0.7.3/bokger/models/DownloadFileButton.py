from bokeh.models import CustomJS
from bokeh.models.widgets import Button
import os

_js_path = os.path.join(os.path.dirname(__file__),"DownloadFile.js")
_js_code = open(_js_path).read()


def downloadFileButton(filepath: str)-> Button:
    with open(filepath, "rb") as f:
        filecontent = f.read()
    button_label = f"Download {os.path.basename(filepath)}"
    button = Button(label=button_label, button_type="success")    
    _js = CustomJS(args=dict(filepath=filepath, filecontent=filecontent),code=_js_code)
    button.js_on_click(_js)
    return button

if __name__ =='__main__':
    from bokeh.io import show
    from bokeh.plotting import output_file
    output_file(filename = "save_file.html", mode='inline')
    
    button = downloadFileButton(__file__)
    show(button)
