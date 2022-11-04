from __future__ import print_function
from terminaltables import SingleTable
from itertools import count
import requests
from dotenv import load_dotenv
import os


def calculates_average_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    if payment_from and payment_to:
        return None
    if not payment_from:
        return payment_to * 0.8
    if not payment_to:
        return payment_from * 1.2


def predict_rub_salary_hh(language):
    salaries = []
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
        hh_response = response.json()
        for vacancie in hh_response["items"]:
            if not vacancie["salary"]:
                continue
            if vacancie["salary"]["currency"] != "RUR":
                salaries.append(None)
            salaries.append(
                calculates_average_salary(
                    vacancie["salary"]["from"], vacancie["salary"]["to"]
                )
            )
        if number == hh_response["pages"]:
            break
    return salaries


def calculates_average_salary_hh(*languages):
    vacancy_languages = dict.fromkeys(*languages)
    for language in vacancy_languages:
        per_job_salaries_hh = predict_rub_salary_hh(language)
        salaries = [
            int(salary) for salary in per_job_salaries_hh
            if salary
        ]
        vacancies_number = len(per_job_salaries_hh)
        processed_vacancies_number = len(salaries)
        average_salary = int(sum(salaries) / len(salaries) if salaries else 0)
        vacancy_languages[language] = {
            "vacancies_found": vacancies_number,
            "vacancies_processed": processed_vacancies_number,
            "average_salary": average_salary
        }
    return vacancy_languages


def predict_rub_salary_sj(superjob_key, language):
    salaries = []
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
        headers = {"X-Api-App-Id": f"{superjob_key}"}
        response = requests.get(
            "https://api.superjob.ru/2.0/vacancies", headers=headers,
            params=params
        )
        response.raise_for_status()
        sj_response = response.json()
        for vacancie in sj_response["objects"]:
            if not vacancie["currency"] == "rub":
                continue
            salaries.append(
                calculates_average_salary(
                    vacancie["payment_from"], vacancie["payment_to"]
                )
            )
        if not sj_response["more"]:
            break
    return salaries


def calculates_average_salary_sj(superjob_key, *languages):
    vacancy_languages = dict.fromkeys(*languages)
    for language in vacancy_languages:
        per_job_salaries_sj = predict_rub_salary_sj(superjob_key, language)
        salaries = [int(salary) for salary in per_job_salaries_sj if salary]
        vacancies_number = len(per_job_salaries_sj)
        processed_vacancies_number = len(salaries)
        average_salary = int(sum(salaries) / len(salaries) if salaries else 0)
        vacancy_languages[language] = {
            "vacancies_found": vacancies_number,
            "vacancies_processed": processed_vacancies_number,
            "average_salary": average_salary
        }
    return vacancy_languages


def converts_statistics_to_table(average_salaries, title):
    column_names = [
        ("Язык программирования", "Вакансий найдено",
         "Вакансий обработано", "Средняя зарплата")
    ]
    for language, statistics in average_salaries.items():
        statistics_vacancies = [numbers for numbers in statistics.values()]
        statistics_vacancies .insert(0, language)
        column_names.append(tuple(statistics_vacancies))
    table_statistics = tuple(column_names)
    table_instance = SingleTable(table_statistics, title)
    return table_instance.table


def main():
    load_dotenv()
    superjob_key = os.getenv("SUPERJOB_KEY")
    languages = [
        "JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "Go"
    ]
    average_salaries_hh = calculates_average_salary_hh(languages)
    average_salaries_sj = calculates_average_salary_sj(superjob_key, languages)
    print(converts_statistics_to_table(
        average_salaries_hh, "HeadHunter Moscow")
    )
    print()
    print(converts_statistics_to_table(average_salaries_sj, "SuperJob Moscow"))


if __name__ == '__main__':
    main()
