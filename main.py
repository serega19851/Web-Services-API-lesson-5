from __future__ import print_function
from terminaltables import SingleTable
from itertools import count
import requests
from dotenv import load_dotenv
import os


def predict_rub_salary_hh(vacancy):
    per_job_salary = []
    for number in count(0):
        params = {
            "text": f"{vacancy}", "per_page": "100", "page": number,
            "area": "1",
            "only_with_salary": True
        }
        response = requests.get(f"https://api.hh.ru/vacancies/", params=params)
        response.raise_for_status()
        for vacancie in response.json()["items"]:
            if vacancie["salary"] is not None:
                if vacancie["salary"]["currency"] != "RUR":
                    per_job_salary.append(None)
                elif (vacancie["salary"]["from"] is not None
                        and vacancie["salary"]["to"] is not None):
                    per_job_salary.append(
                        (vacancie["salary"]["from"] + vacancie["salary"]["to"])
                    )
                elif vacancie["salary"]["from"] is None:
                    per_job_salary.append(vacancie["salary"]["to"] * 0.8)
                elif vacancie["salary"]["to"] is None:
                    per_job_salary.append(vacancie["salary"]["from"] * 1.2)
        if number >= response.json()["pages"]:
            break
    return per_job_salary


def calculates_the_average_salary_hh(*vacancies):
    languages_vacancy = dict.fromkeys(*vacancies)
    for language in languages_vacancy:
        salarys = [
            int(number) for number in predict_rub_salary_hh
            (language) if number is not None
        ]
        number_vacancies = len(predict_rub_salary_hh(language))
        number_of_processed_salaries = len(salarys)
        average_salary = int(sum(salarys) / len(salarys))
        languages_vacancy[language] = {
            "vacancies_found": number_vacancies,
            "vacancies_processed": number_of_processed_salaries,
            "average_salary": average_salary
        }
    return languages_vacancy


def predict_rub_salary_sj(vacancy):
    load_dotenv()
    superjob_key = os.getenv("SUPERJOB_KEY")
    per_job_salary = []
    for number in count(0):
        params = {
            "count": 100, "t": 4, "keyword": vacancy, "catalogues": 48,
            "page": number
        }
        headers = {'X-Api-App-Id': f"{superjob_key}"}
        response = requests.get(
            'https://api.superjob.ru/2.0/vacancies', headers=headers,
            params=params
        )
        for vacancie in response.json()["objects"]:
            if vacancie["currency"] == 'rub':
                if vacancie['payment_from'] and vacancie["payment_to"]:
                    per_job_salary.append(
                        (vacancie['payment_from'] + vacancie["payment_to"])
                        / 2)
                elif (vacancie['payment_from'] == 0
                      and vacancie["payment_to"] == 0):
                    per_job_salary.append(None)
                elif vacancie['payment_from'] == 0:
                    per_job_salary.append(vacancie["payment_to"] * 0.8)
                elif vacancie["payment_to"] == 0:
                    per_job_salary.append(vacancie['payment_from'] * 1.2)
        if response.json()["more"] is False:
            break
    return per_job_salary


def calculates_the_average_salary_sj(*vacancies):
    languages_vacancy = dict.fromkeys(*vacancies)
    for language in languages_vacancy:
        salarys = [
            int(number) for number in predict_rub_salary_sj
            (language) if number is not None
        ]
        number_vacancies = len(predict_rub_salary_sj(language))
        number_of_processed_salaries = len(salarys)
        if len(salarys) == 0:
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": 0
            }
        elif len(salarys):
            average_salary = int(sum(salarys) / len(salarys))
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": average_salary
            }
    return languages_vacancy


def converts_data_nto_table(date_vacancy, title):
    column_names = [
        ('Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата')
    ]
    for vacancie, results in date_vacancy.items():
        job_data = [numbers for numbers in results.values()]
        job_data.insert(0, vacancie)
        column_names.append(tuple(job_data))
    table_data = tuple(column_names)
    table_instance = SingleTable(table_data, title)
    return table_instance.table


def main():
    vacancies = [
        'JavaScript', "Java", "Python", "Ruby", "PHP", "C++", "C#", "Go"
    ]
    sites_titles = ["HeadHunter Moscow", "SuperJob Moscow"]
    salaries_from_different_sites = [
        calculates_the_average_salary_hh(vacancies),
        calculates_the_average_salary_sj(vacancies)
    ]
    for index, site in enumerate(salaries_from_different_sites):
        print(converts_data_nto_table(site, sites_titles[index]))
        print()


if __name__ == '__main__':
    main()
