# https://stackoverflow.com/questions/31824124/is-there-a-way-to-save-bokeh-data-table-content
# https://github.com/bokeh/bokeh/tree/branch-2.3/examples/app/export_csv

from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Button
import os

_js_path = os.path.join(os.path.dirname(__file__),"DownloadCsv.js")
_js_code = open(_js_path).read()

def downloadCsvButton(data, button_label: str = "Download table as csv")-> Button:
    source = ColumnDataSource(data) # same-len dict
    button = Button(label=button_label, button_type="success")
    _js = CustomJS(args=dict(source=source),code=_js_code)
    button.js_on_click(_js)
    return button

if __name__ =='__main__':
    from bokeh.io import show
    from bokeh.plotting import output_file
    output_file(filename = "save_csv.html", mode='inline')
    
    import numpy as np
    
    a = np.arange(4)
    b = *map(lambda x : str(x) + "~~~~", a),
    data = {'bbb':[0,1,2,3],'a': b}
    button = downloadCsvButton(data)

    show(button)
