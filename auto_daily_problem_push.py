import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from msedge.selenium_tools import Edge, EdgeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


def check_daily_challenge_status():
    webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
    edge_options = Options()
    edge_options.use_chromium = True  # 使用 Chromium 版本的 Edge
    edge_options.add_argument("--headless=new")
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")

    print("settings done")

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)
    print("edge opened")

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """
    })
    try:
        driver.get("https://leetcode.cn/accounts/login/?next=%2Fproblemset%2F")
        wait = WebDriverWait(driver, 5)
        time.sleep(5)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        switch_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lc-content > div > div > div > div > div.css-1e4fnko-Container.e19orumq0 > div")))
        switch_button.click()

        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lc-content > div > div > div > div > div:nth-child(3) > div > label > input"))  # 根据实际 ID 或选择器调整
        )
        username_input.send_keys("") # 此处输入用户名

        time.sleep(0.5)
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lc-content > div > div > div > div > div:nth-child(4) > div > label > input"))  # 根据实际 ID 或选择器调整
        )
        password_input.send_keys("") # 此处输入密码

        time.sleep(0.5)
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#lc-content > div > div > div > div > button"))
        )
        login_button.click()
        time.sleep(3)
        entry_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#leetcode-navbar > div.display-none.m-auto.h-\[50px\].w-full.items-center.justify-center.px-6.md\:flex.max-w-\[1200px\] > ul > li.relative.flex.h-full.items-center.text-sm.nav-li-after.border-text-primary.dark\:border-text-primary > a"))  # 替换为登录后特有的选择器
        )
        entry_button.click()

        time.sleep(3)
        print("进入题库")

        today_date = datetime.now().strftime("%Y-%m-%d")
        daily_link = None
        for attempt in range(5):
            try:
                links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "hover\\:text-label-3")))
                for link in links:
                    href = link.get_attribute("href")

                    if today_date in href:
                        print("今日每日一题链接:", href)
                        daily_link = href
                        break

            except Exception as e:
                continue

        if daily_link == None:
            print("未找到今日每日一题链接")
            return None

        driver.get(daily_link)
        wait = WebDriverWait(driver, 10)
        solution_tab = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[data-layout-path='/ts0/tb1'].flexlayout__tab_button_top")
        ))
        solution_tab.click()

        print("成功点击题解按钮")
        wait = WebDriverWait(driver, 5)
        time.sleep(2)

        href_link = None
        for attempt in range(5):
            try:
                elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.no-underline.hover\\:text-blue-s.dark\\:hover\\:text-dark-blue-s.truncate.w-full"))
                )
                href_link = elements.get_attribute("href")
                print("获取的链接:", href_link)
            except Exception as e:
                print(f"尝试第 {attempt + 1} 次重新获取题解链接:", e)
                continue

        if href_link == None:
            print("获取官方题解链接失败")
            return
            
        print("成功获取官方题解")
        #href_link = "https://leetcode.cn/problems/knight-probability-in-chessboard/solutions/1264717/qi-shi-zai-qi-pan-shang-de-gai-lu-by-lee-2qhk/"

        driver.get(href_link)

        time.sleep(1.5)
        Bottons_Selector = ".font-menlo.relative.flex.h-10.cursor-pointer"
        Language_Buttons = driver.find_elements(By.CSS_SELECTOR, Bottons_Selector)

        for element in Language_Buttons:
            text = element.text.strip()
            if text == "C++":
                element.click()
                break
        else:
            print("未找到C++题解代码")
            return

        time.sleep(1)
        code_elements = driver.find_elements(By.CLASS_NAME, "language-cpp")
        if code_elements:
            for element in code_elements:
                if element.text:
                    complete_code = element.text
                    break
        else:
            print("未找到C++题解代码")
            return

        print(complete_code)
        
        from selenium.webdriver.common.keys import Keys 
        textarea_element = driver.find_element(By.CLASS_NAME, "inputarea")
        textarea_element.send_keys(Keys.CONTROL + "a")
        textarea_element.send_keys(Keys.DELETE)
        textarea_element.send_keys(complete_code)
        textarea_element.send_keys(Keys.CONTROL + Keys.END)
        textarea_element.send_keys(Keys.BACKSPACE)

        print("成功清空并输入C++题解代码")

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-e2e-locator='console-submit-button']")
            )
        )
        time.sleep(1)
        submit_button.click()

        time.sleep(3)
        # screenshot_path = "submmit.png"
        # driver.save_screenshot(screenshot_path)
        # print(f"提交完成截图已保存到: {screenshot_path}")
        print("提交成功")


    except Exception as e:
        print("Error:", e)
    finally:
        driver.quit()

print("执行每日一题自动提交")
check_daily_challenge_status()