from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import random

options = webdriver.ChromeOptions()

def main():
    # driver = open_chrome()
    init_graph()


def open_chrome():
    driver = webdriver.Chrome()
    driver.get("")
    driver.maximize_window()
    return driver

def init_graph():

    fig = plt.figure(figsize=(16, 8))
    plt.subplots_adjust(wspace=0, hspace=0, top=0.95, right=0.95, bottom=0.05, left=0.1)


    #length個数分のグラフを設定
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim(-5, 5)
    ax.set_xlim(-20, 10)
    ax.set_xticks([-20, -10, 0])
    ax.set_yticks([-5, 0, 5])
    ax.set_xlabel("time")

    # ax.grid(True)
    ax.plot()

    x = [0]
    y = [0]

    lines, = ax.plot(x, y, linewidth=1, marker=".", markersize=4, color="black")

    times = []
    values = []
    dv_dt = []

    while True:
        
        now = dt.datetime.now()
        value = random.randint(5, 10) 
        
        calced = (value - values[-1]) / (now - times[-1]).total_seconds() / 60 if len(values) > 0 else 0

        times.append(now)
        values.append(value)
        dv_dt.append(calced)

        x = list(map(lambda x: (x - now).total_seconds() / 60 * 10, times))
        dv_dt
        print(x)
        # print(y)
        lines.set_data(x, dv_dt)
        plt.pause(random.random() * 3)



    # 初期値をここでセット





if __name__ == "__main__":
    main()
