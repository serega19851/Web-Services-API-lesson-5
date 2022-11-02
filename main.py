from __future__ import print_function
from terminaltables import SingleTable
from itertools import count
import requests
from dotenv import load_dotenv
import os


def predict_rub_salary_hh(language):
    empty_list = []
    moscow = "1"
    for number in count(0):
        params = {
            "text": f"{language}",
            "per_page": "100",
            "page": number,
            "area": moscow,
            "only_with_salary": True
        }
        response = requests.get("https://api.hh.ru/vacancies/", params=params)
        response.raise_for_status()
        response_json = response.json()
        for vacancie in response_json["items"]:
            if vacancie["salary"]:
                if vacancie["salary"]["currency"] != "RUR":
                    empty_list.append(None)
                elif vacancie["salary"]["from"] and vacancie["salary"]["to"]:
                    empty_list.append(
                        vacancie["salary"]["from"] + vacancie["salary"]["to"]
                    )
                elif vacancie["salary"]["from"] is None:
                    empty_list.append(vacancie["salary"]["to"] * 0.8)
                elif vacancie["salary"]["to"] is None:
                    empty_list.append(vacancie["salary"]["from"] * 1.2)
        if number >= response_json["pages"]:
            break
    per_job_salaries = empty_list
    return per_job_salaries


def calculates_the_average_salary_hh(*languages):
    languages_vacancy = dict.fromkeys(*languages)
    for language in languages_vacancy:
        per_job_salaries_hh = predict_rub_salary_hh(language)
        salary = [
            int(salary) for salary in per_job_salaries_hh
            if salary
        ]
        number_vacancies = len(per_job_salaries_hh)
        number_of_processed_salaries = len(salary)
        average_salary = int(sum(salary) / len(salary))
        if number_of_processed_salaries == 0:
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": 0
            }
        elif number_of_processed_salaries:
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": average_salary
            }
    return languages_vacancy


def predict_rub_salary_sj(language):
    load_dotenv()
    superjob_key = os.getenv("SUPERJOB_KEY")
    per_job_salaries = []
    moscow = 4
    development_programming = 48
    for number in count(0):
        params = {
            "count": 100,
            "t": moscow,
            "keyword": language,
            "catalogues": development_programming,
            "page": number
        }
        headers = {'X-Api-App-Id': f"{superjob_key}"}
        response = requests.get(
            'https://api.superjob.ru/2.0/vacancies', headers=headers,
            params=params
        )
        response_json = response.json()
        for vacancie in response_json["objects"]:
            if vacancie["currency"] == 'rub':
                if vacancie['payment_from'] and vacancie["payment_to"]:
                    per_job_salaries.append(
                        (vacancie['payment_from'] + vacancie["payment_to"])
                        / 2)
                elif (vacancie['payment_from'] == 0
                      and vacancie["payment_to"] == 0):
                    per_job_salaries.append(None)
                elif vacancie['payment_from'] == 0:
                    per_job_salaries.append(vacancie["payment_to"] * 0.8)
                elif vacancie["payment_to"] == 0:
                    per_job_salaries.append(vacancie['payment_from'] * 1.2)
        if response_json["more"] is False:
            break
    return per_job_salaries


def calculates_the_average_salary_sj(*vacancies):
    languages_vacancy = dict.fromkeys(*vacancies)
    for language in languages_vacancy:
        per_job_salaries_sj = predict_rub_salary_sj(language)
        salary = [int(salary) for salary in per_job_salaries_sj if salary]
        number_vacancies = len(per_job_salaries_sj)
        number_of_processed_salaries = len(salary)
        if number_of_processed_salaries == 0:
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": 0
            }
        elif number_of_processed_salaries:
            average_salary = int(sum(salary) / len(salary))
            languages_vacancy[language] = {
                "vacancies_found": number_vacancies,
                "vacancies_processed": number_of_processed_salaries,
                "average_salary": average_salary
            }
    return languages_vacancy


def converts_data_to_table(statistics, title):
    column_names = [
        ('Язык программирования', 'Вакансий найдено',
         'Вакансий обработано', 'Средняя зарплата')
    ]
    for language, results in statistics.items():
        statistics_vacancies = [numbers for numbers in results.values()]
        statistics_vacancies .insert(0, language)
        column_names.append(tuple(statistics_vacancies))
    table_data = tuple(column_names)
    table_instance = SingleTable(table_data, title)
    return table_instance.table


def main():
    languages = [
        'JavaScript', "Java", "Python", "Ruby", "PHP", "C++", "C#", "Go"
    ]
    average_salaries_hh = calculates_the_average_salary_hh(languages)
    average_salaries_sj = calculates_the_average_salary_sj(languages)
    print(converts_data_to_table(average_salaries_hh, "HeadHunter Moscow"))
    print()
    print(converts_data_to_table(average_salaries_sj, "SuperJob Moscow"))


if __name__ == '__main__':
    main()
