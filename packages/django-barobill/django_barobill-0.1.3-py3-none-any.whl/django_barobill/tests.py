import datetime

from django.test import TestCase
from django.utils import timezone

from django_barobill.choices import BankAccountBank, BankAccountCollectCycle, BankAccountAccountType
from django_barobill.models import Partner, BankAccount
from django_barobill.parsers import bank_account_log_parser


# Create your tests here.
class TestBankAccount(TestCase):
    def setUp(self):
        self.partner = Partner.objects.create(
            name='지구하다ERP',
            brn='2978601887',
            api_key='0830C49B-71EA-44E0-81E0-DAAD883B3FC9',
            userid='cuhong',
            dev=True
        )
        self.bank = BankAccountBank.HANA
        self.account_no = '26091002164604'
        self.bank_account = BankAccount.objects.create(
            partner=self.partner,
            collect_cycle=BankAccountCollectCycle.MINUTE10,
            bank=self.bank,
            account_type=BankAccountAccountType.C,
            account_no=self.account_no,
        )

    def test_get_yesterday_log(self):
        date_string = (timezone.localdate() - datetime.timedelta(days=0)).strftime('%Y%m%d')
        log_list = []
        page = 1
        while True:
            result = self.bank_account.get_daily_log(date_string, page)
            log_list += [] if result.BankAccountLogList is None else result.BankAccountLogList.BankAccountLogEx2
            if result.MaxPageNum == page:
                break
            page += 1
        for log in log_list:
            print(bank_account_log_parser(log))

    def test_update_today_log(self):
        self.bank_account.update_today_log()

ba = BankAccount.objects.first()
ba.update_yesterday_log()