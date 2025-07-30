import datetime

from django_barobill.utils import KST


def bank_account_log_parser(item):
    """
    BankAccountLogEx2를 데이터베이스에 적재할 수 있는 형태로 파싱한다.
    :param item: BankAccountLogEx2를
    :return: BankAccountTransaction
    """
    from django_barobill.choices import BankAccountTransactionDirection
    return dict(
        trans_direction={
            "입금": BankAccountTransactionDirection.Deposit,
            "출금": BankAccountTransactionDirection.Withdraw,
            "기타": BankAccountTransactionDirection.ETC,
        }.get(item.TransDirection),
        deposit=int(item.Deposit),
        withdraw=int(item.Withdraw),
        balance=int(item.Balance),
        trans_dt=KST.localize(datetime.datetime.strptime(item.TransDT, "%Y%m%d%H%M%S")),
        trans_type=item.TransType,
        trans_office=item.TransOffice,
        trans_remark=item.TransRemark,
        mgt_remark_1=item.MgtRemark1,
        trans_ref_key=item.TransRefKey,
        memo=item.Memo,
    )