__author__ = "chaoweichen26@gmail.com"

import numpy as np
import json
from bokeh.layouts import column, row
from bokeh import models
from bokeh.plotting import figure, output_file, show, save
from .models.DownloadCsvButton import downloadCsvButton
from .models.DownloadFileButton import downloadFileButton

from .models.CopyToClipboardButton import copyToClipboardButton

from .utilities.TimeStamp import get_timestamp_str, get_datetime_str, _datetime_format
from rich import print
import inspect


class Bokger:
    def __init__(self):
        self.layoutDOM: list = []
        self.startTime = get_datetime_str()

    def log_source(self, co):
        _src = inspect.getsource(co)
        self.log_pretext(_src)

    def log_div(self, message: str, **_styles):
        print(message)
        dom = models.Div(
            text=message,
            width=1000,
        )
        button = copyToClipboardButton(message)
        self.layoutDOM.append(row(dom, button, sizing_mode="scale_width"))

    def log_image(self, im0: np.array):
        dw, dh = im0.shape

        # https://discourse.holoviz.org/t/custom-image-hovertool-with-mask-labels/1377
        hover_tool_tooltips = [
            ("(x,y)", "($x,$y)"),
            ("value", "@image"),
        ]
        dom = figure(
            x_range=(0, dw),
            y_range=(0, dh),
            width=500,
            height=500,
            tools="pan,wheel_zoom,reset,hover,crosshair,save",
            tooltips=hover_tool_tooltips,
            active_drag="pan",
            active_scroll="wheel_zoom",
        )
        dom.toolbar.logo = None

        dom.image(
            image=[im0], x=0, y=0, dw=dw, dh=dh, palette="Greys256", level="image"
        )
        self.layoutDOM.append(dom)

    def log_table(self, table):
        print(table)
        source = models.ColumnDataSource(table)  # table should be same length dict
        columns = []
        for col in table.columns:
            col_type = table[col].dtype
            if np.issubdtype(col_type, np.datetime64):
                _formatter = models.DateFormatter(format=_datetime_format)
                tc = models.TableColumn(field=col, title=col, formatter=_formatter)
            else:
                tc = models.TableColumn(field=col, title=col)
            columns.append(tc)
        # https://docs.bokeh.org/en/latest/docs/reference/models/widgets/tables.html
        data_table = models.DataTable(
            source=source, columns=columns, width=1600, sizing_mode="scale_both"
        )
        button = downloadCsvButton(table)
        dom = row(data_table, button, sizing_mode="scale_width")
        self.layoutDOM.append(dom)

    def log_file(self, filepath: str):
        print(filepath)
        filepath_dom = models.PreText(
            text=filepath,
            width=1000,
        )
        button = downloadFileButton(filepath)
        dom = row(filepath_dom, button, sizing_mode="scale_width")
        self.layoutDOM.append(dom)

    def log(self, *domlikes):
        for domlike in domlikes:
            self._log(domlike)

    def _log(self, domlike):
        if isinstance(domlike, models.LayoutDOM):
            self.layoutDOM.append(domlike)
        elif isinstance(domlike, str):
            _str = domlike
            timestamped_msg = f"{_str} # {get_timestamp_str()}"
            self.log_pretext(timestamped_msg)
        else:
            obj = domlike
            try:
                _str: str = json.dumps(obj, indent=2, separators=(",", ": "))
            except:
                _str: str = repr(obj)
            timestamped_msg = f"{_str} # {get_timestamp_str()}"
            self.log_pretext(timestamped_msg)

    def log_pretext(self, message):
        print(message)
        dom = models.PreText(
            text=message,
            width=1000,
        )
        button = copyToClipboardButton(message)
        self.layoutDOM.append(row(dom, button, sizing_mode="scale_width"))

    def show(self, html_path: str):
        """save and open browser"""
        html_path = f"{html_path}.{self.startTime}.html".replace("/", "").replace(
            ":", ""
        )
        output_file(filename=html_path, mode="inline")

        show(column(*self.layoutDOM))

    def save(self, html_path: str):
        """save only"""
        output_file(filename=html_path, mode="inline")
        save(column(*self.layoutDOM))


logger = Bokger()
