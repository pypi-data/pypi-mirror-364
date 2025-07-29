# -*- coding: utf-8 -*-
import numpy as np


def t2c(t_c, gamma=1.402, R=8.3145, M=0.02896):
    return np.sqrt(gamma * R * (t_c + 273.15) / M)
