from banki_ru.database import BankiRuBank, BankiRuInsurance, BankiRuMfo, BankiRuBroker
from banki_ru.schemes import BankTypes
from common.database import SessionLocal


def get_bank_list(bank_site: BankTypes) -> list[BankiRuBank]:
    with SessionLocal() as db:
        match bank_site:
            case BankTypes.bank | BankTypes.news:
                bank_list = db.query(BankiRuBank).order_by(BankiRuBank.bank_id).all()
            case BankTypes.insurance:
                bank_list = db.query(BankiRuInsurance).order_by(BankiRuInsurance.bank_id).all()
            case BankTypes.mfo:
                bank_list = db.query(BankiRuMfo).order_by(BankiRuMfo.bank_id).all()
            case BankTypes.broker:
                bank_list = db.query(BankiRuBroker).order_by(BankiRuBroker.bank_id).all()
            case _:
                raise NotImplementedError
    return bank_list


def create_banks(bank_list: list[BankiRuBank]) -> None:
    with SessionLocal() as db:
        db.add_all(bank_list)
        db.commit()
