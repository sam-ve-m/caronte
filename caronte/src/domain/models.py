from dataclasses import dataclass


@dataclass()
class User:
    name: str
    cpf: str
    email: str
    phone: str
    zip_code: str
    street_name: str
    number: int
    neighborhood: str
    city: str
    state: int
    birth_date: str
    income: str
