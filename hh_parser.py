import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


def parse_salary_for_sorting(salary_str):
    clean_str = re.sub(r'\s+', '', salary_str.replace('\u202f', '').replace('\xa0', ''))
    numbers = re.findall(r'\d+', clean_str)

    if numbers:
        return max(int(num) for num in numbers)
    return 0


def get_html(url):
    service = Service("data/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        try:
            cook_btn = driver.find_element(By.CSS_SELECTOR, '[data-qa="cookies-policy-informer-accept"]')
            cook_btn.click()
            button = driver.find_element(By.CSS_SELECTOR, '[data-qa="vacancy-item-desktop"]')
            button.click()
        except Exception as e:
            print("Не удалось кликнуть по элементам, продолжаем парсинг...", e)

        html = driver.page_source
        return html

    except Exception as ex:
        print("Ошибка при получении HTML:", ex)
        return None

    finally:
        driver.quit()
        print("Браузер закрыт.\n" + "-" * 40)


def main():
    html = get_html("https://hh.ru")

    if html:
        soup = BeautifulSoup(html, "lxml")
        parsed_vacancies = []

        titles = soup.find_all(attrs={"data-qa": "vacancy_of_the_day_title"})

        for title_element in titles:
            title_text = title_element.get_text(strip=True)

            card = title_element.find_parent("div", class_=lambda c: c and "magritte-card" in c)
            if not card:
                continue

            salary_element = card.find(attrs={"data-qa": "vacancy_of_the_day_compensation"})
            salary_text = salary_element.get_text(strip=True) if salary_element else "З/п не указана"

            company_element = card.find('a', class_=lambda c: c and 'bloko-link' in c and 'kind-secondary' in c)
            address_text = company_element.get_text(strip=True) if company_element else "Адрес не указан"

            parsed_vacancies.append({
                "title": title_text,
                "address": address_text,
                "salary": salary_text,
                "sort_value": parse_salary_for_sorting(salary_text)
            })

        # Сортировка по убыванию зарплаты
        parsed_vacancies.sort(key=lambda x: x["sort_value"], reverse=True)

        with open("vacancies.txt", "w", encoding="utf-8") as file:
            header = "Список найденных вакансий:"
            print(header)
            file.write(header + "\n")

            for v in parsed_vacancies:
                vacancy_line = f"\n{v['title']} ({v['address']}) - {v['salary']}"

                print(vacancy_line)  # Вывод в терминал
                file.write(vacancy_line + "\n")  # Запись в файл

        print(f"\nРезультаты успешно сохранены в файл 'vacancies.txt'")

    else:
        print("Не удалось получить HTML код страницы.")


if __name__ == "__main__":
    main()
