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

target_url = "ここにurlを入力する"
iframe_css = "#Stowv2MeridianBlock"
stow_breakdown_css = ".css-1g8dw35"
clustor_css = "tbody > .css-xlf10u"
aisle_css = "tbody > tr > .css-y5ti3q > span"
aisle_elem_css = "tbody > tr > .css-af10 > span"
back_css = ".css-44tx1c"


clustors = ["A","B","C","D","E","G","H","J","K","L","M","P"]
aisle_num = 22

history = {
    "inducted":     [[] for _ in range(aisle_num * len(clustors))],
    "stowed":       [[] for _ in range(aisle_num * len(clustors))],
    "total":        [[] for _ in range(aisle_num * len(clustors))],
    "dtotal_by_dt": [[] for _ in range(aisle_num * len(clustors))],
    "datetime":     [[] for _ in range(len(clustors))]
}

options = webdriver.ChromeOptions()

def main():
    driver = open_chrome()
    print(init_graph)
    fig, ls, x, ys = init_graph(len(clustors) * aisle_num)

    while True:
        driver.refresh()
        print("move_to_stow_breakdown")
        move_to_stow_breakdown(driver, iframe_css, stow_breakdown_css)
        print("find_iframe")
        iframe = find_iframe(driver, iframe_css)

        print("switch_to_iframe")
        driver.switch_to.frame(iframe)
        print("wait 30 sec...")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, clustor_css)))
        print("wait 30 sec... done")
        times = len(driver.find_elements(By.CSS_SELECTOR, clustor_css))
        for i in range(times):
            print("times: ", i, "/", times)
            draw_graph(driver, ls, x, ys, i)


def open_chrome():
    driver = webdriver.Chrome()
    driver.get(target_url)
    driver.maximize_window()
    return driver

def find_iframe(driver, css):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    return driver.find_element(By.CSS_SELECTOR, css)

def get_element_in_iframe(driver, iframe, css):
    driver.switch_to.frame(iframe)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    elements = driver.find_elements(By.CSS_SELECTOR, css)

    result = []
    for i, el in enumerate(elements):
        if i % 3 == 1:
            # print(el.text)
            result.append(el.text)

    driver.switch_to.default_content()
    return result

def move_to_stow_breakdown(driver, iframe_css, elem_css):
    iframe = find_iframe(driver, iframe_css)
    driver.switch_to.frame(iframe)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, elem_css)))
    elements = driver.find_elements(By.CSS_SELECTOR, elem_css)

    for el in elements:
        span = el.find_element(By.CSS_SELECTOR, "span")
        # print("move_to_stow_breakdown, span", span.text)
        if span.text == "Stow Breakdown":
            time.sleep(3)
            el.click()
            break
    driver.switch_to.default_content()
    time.sleep(1)

def select_cluster(driver, clustor_css, aisle_css, aisle_elem_css, i):
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, clustor_css)))
    times = len(driver.find_elements(By.CSS_SELECTOR, clustor_css))
    
    if i != times - 1:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, clustor_css)))

        # クラスターを選択
        els = driver.find_elements(By.CSS_SELECTOR, clustor_css)
        els[i].click()
        time.sleep(1)

        # クラスターの中のaisleの値を取得
        dict = get_aisle_and_values(driver, aisle_css, aisle_elem_css, i)

        # クラスター一覧に画面を戻す
        click_back_btn(driver, back_css)
        print(dict)

        return dict
    
    else:
        print("select_cluster: Total行をskip中 ...")
        return None



def get_aisle_and_values(driver, aisle_css, aisle_elem_css, i):
    print("get_aisle_and_values !!")
    time.sleep(2)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, aisle_css)))
    aisle_els = driver.find_elements(By.CSS_SELECTOR, aisle_css)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, aisle_elem_css)))
    aisle_elem_els = driver.find_elements(By.CSS_SELECTOR, aisle_elem_css)
    
    aisles      = [el.text for el in aisle_els]
    aisle_elems = [el.text for el in aisle_elem_els]
    inducted    = [el for i, el in enumerate(aisle_elems) if i % 12 == 2]
    stowed      = [el for i, el in enumerate(aisle_elems) if i % 12 == 4]

    if aisles[0][0] != clustors[i]:
        print("Error!! skip this cluster:", clustors[i])
    
    now = dt.datetime.now()

    return {"aisles": aisles, "inducted": inducted, "stowed": stowed, "datetime": now }

def click_back_btn(driver, back_css):
    # print("click_back_btn", back_css)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, back_css)))
    back_btn = driver.find_element(By.CSS_SELECTOR, back_css)
    back_btn.click()


def init_graph(length):
    
    fig = plt.figure(figsize=(16, 8))
    plt.subplots_adjust(wspace=0, hspace=0, top=0.95, right=0.95, bottom=0.05, left=0.05)

    axs = []
    #length個数分のグラフを設定
    for i in range(length):
        ax = fig.add_subplot(12, 22, i+1)
        ax.set_ylim(0, 100)
        ax.set_xlim(-20, 0)
        ax.set_xticks([])
        ax.set_yticks([])
        if i % 22 == 0:
            ax.set_yticks([0,30,60])
            ax.set_ylabel(clustors[int(i/22)])
        # ax.set_title("title" + str(i))
        if i >= 11 * 22:
            ax.set_xticks([-10, 0])
            ax.set_xlabel("time")
        # ax.grid(True)
        axs.append(ax)
        ax.plot()


    # 初期値をここでセット
    x  = [[i] for i in range(11)]
    ys = [[0] * 11 for _ in range(length)]

    ls = []
    for i in range(length):
        lines, = axs[i].plot(x, ys[i], linewidth=1, marker=".", markersize=4, color="black")
        ls.append(lines)
    
    return fig, ls, x, ys

def draw_graph(driver, ls, x, ys, i):

    clustor = select_cluster(driver, clustor_css, aisle_css, aisle_elem_css, i)
    print("----------- cluster data was fetched ! ------------- \n", clustor)
    if clustor is None:
        return
    
    aisles = clustor["aisles"]
    inducted = clustor["inducted"]
    stowed = clustor["stowed"]
    dt_fetch = clustor["datetime"]

    for j, aisle in enumerate(aisles):
        cl = aisle[0]
        num = int(aisle[1:])

        idx = clustors.index(cl) * 22 + num - 1

        el_inducted = int(inducted[j])
        el_stowed  = int(stowed[j])
        el_total = el_inducted + el_stowed
        

        result = 0

        if len(history["datetime"][i]) > 1 and len(history["total"][idx]) > 0:
            previous_total    = history["total"][idx][-1]
            previous_datetime = history["datetime"][i][-1]

            delta_total = el_total - previous_total
            delta_time  = (dt_fetch - previous_datetime).total_seconds() / 60

            print("--------------- Error divided by zero ---------------")
            print("total: ", el_total)
            print("previous: ", previous_total)
            print("diff", delta_total)
            print("now: ", dt_fetch)
            print("previous: ", previous_datetime)
            print("diff", delta_time)

            result = delta_total / delta_time


        history["inducted"][idx].append(el_inducted)
        history["stowed"][idx].append(el_stowed)
        history["total"][idx].append(el_total)
        history["dtotal_by_dt"][idx].append(result)
        if j == 0:
            history["datetime"][i].append(dt_fetch)

        print("now :",dt_fetch)

        print(history["inducted"][idx])
        print(history["stowed"][idx])
        print(history["datetime"][i])
        print("", history["dtotal_by_dt"][idx].append(result))

        # ys[idx].pop(0) 
        # ys[idx].append(result)
        x = list(map(lambda t: (dt_fetch - t).total_seconds() / 60 , history["datetime"][i]))
        print("x軸:", x)
        print("y軸:", history["dtotal_by_dt"][idx])

        for l_i in range(len(ls)):
            ls[l_i].set_data(x, history["dtotal_by_dt"][l_i])

    print(history)
    plt.pause(1)

    return ls, x, ys


if __name__ == "__main__":
    main()
