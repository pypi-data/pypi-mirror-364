# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np


def copy2clip(val):
    """
    Copies a value to the system clipboard.

    Parameters:
    val (str or iterable): The value to be copied to the clipboard. Can be a string or an iterable.

    Returns:
    None
    """
    import pandas as pd

    if isinstance(val, str):
        df = pd.DataFrame([val])
    else:
        df = pd.DataFrame(val)
    df.to_clipboard(index=False, header=False)


def fig2clip():
    """
    Copies the current matplotlib figure to the system clipboard.

    Returns:
    None
    """
    from PyQt5.QtWidgets import QApplication

    # from PyQt5.QtGui import QPixmap

    fig = plt.gcf()
    pixmap = fig.canvas.grab()
    QApplication.clipboard().setPixmap(pixmap)
    print("Figure %d copied" % fig.number)


def clip2np():
    """
    Reads the content of the system clipboard and converts it to a numpy array.

    Returns:
    numpy.ndarray: The clipboard content as a numpy array.
    """
    import pandas as pd

    df = np.array(pd.read_clipboard(header=None)).squeeze()
    print(repr(df))
    return df


def fig2xls(axs):
    """
    Copies the data from the lines in the axes to the clipboard to be pasted into Excel.

    Parameters:
    axs (numpy.ndarray): The axes from which the data will be copied.

    Returns:
    None
    """
    import pandas as pd

    df = pd.DataFrame()
    for i, ax in enumerate(axs.flatten()):
        lines = ax.get_lines()
        for line in lines:
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            df[f"X{i}"] = pd.Series(x_data)
            df[f"Y{i}"] = pd.Series(y_data)
    df.to_clipboard(index=False, header=True)
