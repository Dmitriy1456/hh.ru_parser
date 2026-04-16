import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


def get_html(url):
    service = Service("data/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        button = driver.find_element(By.CSS_SELECTOR, '[data-qa="vacancy-item-desktop"]')
        cook_btn = driver.find_element(By.CSS_SELECTOR, '[data-qa="cookies-policy-informer-accept"]')
        cook_btn.click()
        button.click()

        html = driver.page_source
        return html

    except Exception as ex:
        print(ex)

    finally:
        driver.quit()
        print("Работа завершена.")


def main():
        html = get_html("https://hh.ru")
        print(html)

        if html:
            soup = BeautifulSoup(html, "lxml")

            vacancies = soup.find_all(attrs={"data-qa": "profession-item-tile-title"})

            print("Список найденных вакансий:")
            for vacancy in vacancies:
                print(f"- {vacancy.get_text(strip=True)}")
        else:
            print("Не удалось получить HTML код страницы.")

if __name__ == "__main__":
    main()