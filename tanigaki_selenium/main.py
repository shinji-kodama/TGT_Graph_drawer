from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

target_url = "ここにurlを入力する"
cycle_off_css = ".css-9z1d21"

cycle1_css = ".css-44tx1c"

iframe_css = "#Stowv2MeridianBlock"
stow_breakdown_css = ".css-1g8dw35"
cluster_css = "tbody > .css-xlf10u"
clusters_css = "tbody > .css-xlf10u > .css-y5ti3q"
aisle_css = "tbody > tr > .css-y5ti3q > span"
aisle_elem_css = "tbody > tr > .css-af10 > span"
back_css = ".css-44tx1c"

all_clusters = ["A","B","C","D","E","G","H","J","K","L","M","P"]
clusters = []
max_cluster_num = len(all_clusters)
aisle_num = 22

history = {
    "inducted":     [[] for _ in range(aisle_num * max_cluster_num)],
    "stowed":       [[] for _ in range(aisle_num * max_cluster_num)],
    "total":        [[] for _ in range(aisle_num * max_cluster_num)],
    "dtotal_by_dt": [[] for _ in range(aisle_num * max_cluster_num)],
    "datetime":     [[] for _ in range(max_cluster_num)]
}

options = webdriver.ChromeOptions()

def main():
    number = input("CYCLEの値を入力してください(1, 2, 3) : ")
    print("number: ", number)
    driver = open_chrome()

    move_to_stow_breakdown(driver, iframe_css, stow_breakdown_css)
    enter_iframe(driver, iframe_css)
    select_cycle(driver, cycle_off_css, int(number - 1))
    get_clusters(driver, clusters_css)

    fig, ls, ls_i, ls_h, x, ys  = init_graph(len(all_clusters) * aisle_num)

    while True:
        # driver.refresh()
        times = get_clusters_times(driver, cluster_css)
        for i in range(times):
            print("times: ", i, "/", times, "draw_graph ...")
            draw_graph(driver, ls, ls_i, ls_h, x, ys, i)

def open_chrome():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(target_url)
    driver.maximize_window()
    return driver

def select_cycle(driver, css, n):
    el = driver.find_elements(By.CSS_SELECTOR, css)
    el[1].click()
    divs = driver.find_elements(By.CSS_SELECTOR, "body > div")
    target = divs[len(divs) - 1]
    # print('エレメント：', target)
    time.sleep(1)
    elements = target.find_elements(By.CSS_SELECTOR, cycle1_css)
    time.sleep(1)
    # print(elements[n].text)
    elements[n].click()


def find_iframe(driver, css):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    return driver.find_element(By.CSS_SELECTOR, css)

def get_element_in_iframe(driver, iframe, css):
    driver.switch_to.frame(iframe)
    elements = get_elems_by_css(driver, css, 10)

    result = []
    for i, el in enumerate(elements):
        if i % 3 == 1:
            result.append(el.text)

    driver.switch_to.default_content()
    return result

def move_to_stow_breakdown(driver, iframe_css, elem_css):

    enter_iframe(driver, iframe_css)
    elements = get_elems_by_css(driver, elem_css, 10)

    for el in elements:
        span = el.find_element(By.CSS_SELECTOR, "span")
        if span.text == "Stow Breakdown":
            time.sleep(3)
            el.click()
            break
    driver.switch_to.default_content()
    time.sleep(1)

def enter_iframe(driver, iframe_css):
    iframe = find_iframe(driver, iframe_css)
    driver.switch_to.frame(iframe)

def get_clusters_times(driver, cluster_css):
    try:
        times = len(get_elems_by_css(driver, cluster_css, 5))
        return times
    except Exception as e:
        # print("error:", e)
        driver.refresh()
        move_to_stow_breakdown(driver, iframe_css, stow_breakdown_css)
        enter_iframe(driver, iframe_css)
        return get_clusters_times(driver, cluster_css)

def get_clusters(driver, css):
    els = get_elems_by_css(driver, css, 5)
    for el in els:
        clusters.append(el.text)
    
def get_elem_by_css(driver, css, sec):
    wait = WebDriverWait(driver, sec)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    return driver.find_element(By.CSS_SELECTOR, css)

def get_elems_by_css(driver, css, sec):
    wait = WebDriverWait(driver, sec)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
    return driver.find_elements(By.CSS_SELECTOR, css)

def select_cluster(driver, cluster_css, aisle_css, aisle_elem_css, i):
    times = len(get_elems_by_css(driver, cluster_css, 30))
    # print("times: ", times)
    
    if i != times - 1:
        # print("select_cluster : ", i, "/", times - 1)
        # クラスターを選択
        els = get_elems_by_css(driver, cluster_css, 10)
        els[i].click()
        time.sleep(1)
        # クラスターの中のaisleの値を取得
        dict = get_aisle_and_values(driver, aisle_css, aisle_elem_css, i)
        click_back_btn(driver, back_css)
        return dict
    else:
        return None

def get_aisle_and_values(driver, aisle_css, aisle_elem_css, i):
    time.sleep(2)
    # try:
    aisle_els = get_elems_by_css(driver, aisle_css, 10)
    aisle_elem_els = get_elems_by_css(driver, aisle_elem_css, 10)
    
    aisles      = [el.text for el in aisle_els]
    # print("aisle_els: ", aisle_els)
    aisle_elems = [el.text for el in aisle_elem_els]
    # print("aisle_elems: ", aisle_elems)
    inducted    = [el for i, el in enumerate(aisle_elems) if i % 12 == 2]
    stowed      = [el for i, el in enumerate(aisle_elems) if i % 12 == 4]

    print("aisles: ",i,"番目, cluster: ", clusters[i])
    print("aisles: ", aisles[0][0])
    # print("clusters[i]: ", clusters[i])

    if aisles[0][0] != clusters[i]:
        # print("Error!! skip this cluster:", clusters[i])
        return None
    
    now = dt.datetime.now()

    return {"aisles": aisles, "inducted": inducted, "stowed": stowed, "datetime": now }
        
    # except Exception as e:
    #     print("error:", e)
    #     return None

def click_back_btn(driver, back_css):
    back_btn = get_elem_by_css(driver, back_css, 10)
    back_btn.click()


def init_graph(length):
    # print("引数の配列 length: ", length)
    
    fig = plt.figure(figsize=(18, 8))
    plt.subplots_adjust(wspace=0, hspace=0, top=0.95, right=0.95, bottom=0.05, left=0.05)

    axs = []
    #length個数分のグラフを設定
    for i in range(length):
        # print(i)
        ax = fig.add_subplot(len(all_clusters), 22, (22 * int(i/22)) + 22 - (i % 22))
        ax.set_ylim(0, 15)
        ax.set_xlim(-10, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        if i % 22 == 21:
            # print("1個目のif : ", i)
            ax.set_yticks([0,10])
            ax.set_ylabel(all_clusters[int(i/22)])
            # print(all_clusters[int(i/22)])
        # ax.set_title("title" + str(i))
        if i >= (len(all_clusters) - 1) * 22:
            # print("2個目のif : ", i)
            ax.set_xticks([-8, -4, 0])
            ax.set_xlabel(str(i - 22 * (len(all_clusters) - 1) + 1))
            # print(str(i - 22 * (len(all_clusters) - 1) + 1))
        # ax.grid(True)
        axs.append(ax)
        ax.plot()

    # 初期値をここでセット
    x  = [0]
    ys = [[0] for _ in range(length)]
    x_i = [0]
    ys_i = [[0] for _ in range(length)]
    x_h = [-10, 1]
    y_h = [10, 10]

    ls = []
    ls_i = []
    ls_h = []
    for i in range(length):
        lines,  = axs[i].plot(x, ys[i], linewidth=2, marker="o", markersize=4, color="darkred")
        lines_i, = axs[i].plot(x_i, ys_i[i], linewidth=1, marker=".", markersize=2, color="skyblue", linestyle="dotted")
        lines_h, = axs[i].plot(x_h, y_h, linewidth=1, marker="None", color="gray", linestyle="dashed")
        ls.append(lines)
        ls_i.append(lines_i)
        ls_h.append(lines_h)
    
    # print("init graph was finished !")
    
    return fig, ls, ls_i, ls_h, x, ys

def draw_graph(driver, ls, ls_i, ls_h, x, ys, i):
    # print("draw graph was called ! :", i)

    cluster = select_cluster(driver, cluster_css, aisle_css, aisle_elem_css, i)
    if cluster is None:
        print("cluster is Total, skip it ...")
        return
    # print("----------- cluster ", clusters[i], "data was fetched ! ------------- \n", cluster)
    
    aisles = cluster["aisles"]
    inducted = cluster["inducted"]
    stowed = cluster["stowed"]
    dt_fetch = cluster["datetime"]

    for j, aisle in enumerate(aisles):
        cl = aisle[0]
        num = int(aisle[1:])

        idx = all_clusters.index(cl) * 22 + num - 1

        el_inducted = int(inducted[j])
        el_stowed  = int(stowed[j])
        el_total = el_inducted + el_stowed

        result = 0 if len(history["dtotal_by_dt"][idx]) == 0 else history["dtotal_by_dt"][idx][-1]

        if len(history["datetime"][i]) > 1 and len(history["total"][idx]) > 0:

            previous_total    = history["total"][idx][-1]
            previous_datetime = 0
            if j == 0:
                previous_datetime = history["datetime"][i][-1]
            else:
                previous_datetime = history["datetime"][i][-2]

            delta_total = el_total - previous_total
            delta_time  = (dt_fetch - previous_datetime).total_seconds() / 60
            result = delta_total / delta_time


        history["inducted"][idx].append(el_inducted)
        history["stowed"][idx].append(el_stowed)
        history["total"][idx].append(el_total)
        history["dtotal_by_dt"][idx].append(result)
        if j == 0:
            history["datetime"][i].append(dt_fetch)

        # print("インダクション：", history["inducted"][idx])
        # print("ストー済み:", history["stowed"][idx])
        # print("時刻：", history["datetime"][i])

        # ys[idx].pop(0) 
        # ys[idx].append(result)
        x = list(map(lambda t: (t - dt_fetch).total_seconds() / 60 , history["datetime"][i]))
        # print("x", idx, ":", x)
        # print("y", idx, ":", history["dtotal_by_dt"][idx])
        ls[idx].set_data(x, history["dtotal_by_dt"][idx])
        ls_i[idx].set_data(x, list(map(lambda x: x / 10, history["inducted"][idx])))

    plt.pause(0.1)

if __name__ == "__main__":
    main()
