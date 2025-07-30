import datetime
from typing import Optional

from django.db import models
from django.utils import timezone
from zeep import Client, Transport

from django_barobill.choices import BankAccountCollectCycle, BankAccountBank, BankAccountAccountType, BankAccountTransactionDirection
from django_barobill.errors import BarobillAPIError, BarobillError
from django_barobill.parsers import bank_account_log_parser


class BankHelper:
    def __init__(self, partner):
        self.partner = partner
        self.client = self._get_client()

    def _get_client(self):
        if self.partner.dev:
            endpoint = "https://testws.baroservice.com/BANKACCOUNT.asmx?wsdl"
        else:
            endpoint = "https://ws.baroservice.com/BANKACCOUNT.asmx?wsdl"
        transport = Transport(timeout=60)
        return Client(endpoint, transport=transport)

    def get_bank_account_management_url(self):
        return self.client.service.GetBankAccountManagementURL(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            ID=self.partner.userid,
            PWD=''
        )

    def get_bank_account_list(self, avail_only: bool):
        response = self.client.service.GetBankAccountEx(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            AvailOnly=1 if avail_only is True else 0,
        )
        if response is None:
            return []
        return response

    def register_bank_account(
            self,
            alias: str,
            collect_cycle: BankAccountCollectCycle,
            bank: BankAccountBank,
            account_type: BankAccountAccountType,
            account_no: str,
            password: str,
            usage: Optional[str] = None,
            web_id: Optional[str] = None,
            web_pwd: Optional[str] = None,
            identity_num: Optional[str] = None
    ):
        """
        신규 계좌를 등록한다.
        :param alias: 별칭
        :param collect_cycle: 수거주기
        :param bank: 은행
        :param account_type: 법인/개인계좌 여부
        :param account_no: 계좌번호
        :param password: 계좌 비밀번호
        :param usage: (선택)적요
        :param web_id:  (선택)간편조회 아이디
        :param web_pwd: (선택)간편조회 비밀번호
        :param identity_num: (선택)간편조회 사업자등록번호 혹은 생년월일
        :return: 생성된 BankAccount 인스턴스
        """
        result = self.client.service.RegistBankAccount(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            CollectCycle=collect_cycle,
            Bank=bank,
            BankAccountType=account_type,
            BankAccountNum=account_no,
            BankAccountPwd=password,
            WebId=web_id,
            WebPwd=web_pwd,
            IdentityNum=identity_num,
            Alias=alias,
            Usage=usage,
        )
        if result != 1:
            raise BarobillAPIError(result)
        account, created = BankAccount.objects.update_or_create(
            partner=self.partner, account_no=account_no, defaults=dict(
                collect_cycle=collect_cycle, bank=bank, account_type=account_type, alias=alias, usage=usage, is_stop=False
            )
        )
        return account

    def update_bank_accounts(self):
        account_list = self.get_bank_account_list(avail_only=False)
        account_no_list = [acc.BankAccountNum for acc in account_list]
        self.partner.bankaccount_set.filter(
            account_no__in=account_no_list
        ).update(is_stop=False, stop_date=None, )
        self.partner.bankaccount_set.exclude(
            account_no__in=account_no_list
        ).update(is_stop=True, stop_date=timezone.localdate())


class PartnerManager(models.Manager):
    def register_partner(self, name, brn, api_key, userid, dev=False):
        """
        신규 파트너를 등록한다.
        :param name: 파트너사명
        :param brn: 바로빌에 등록한 파트너 사업자등록번호
        :param api_key: 바로빌에서 발급한 파트너 api_key
        :param userid: 바로빌에서 발급한 파트너 Id
        :param dev: 개발모드 여부
        :return: Partner
        """
        partner, created = self.get_or_create(
            brn=brn, userid=userid, defaults=dict(name=name, api_key=api_key, dev=dev)
        )
        return partner


class Partner(models.Model):
    class Meta:
        verbose_name = '파트너'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['brn', 'userid', 'dev'], name='unique_partner_brn_userid'),
        ]

    objects = PartnerManager()
    name = models.CharField(max_length=255, unique=True, verbose_name='파트너사명')
    brn = models.CharField(max_length=10, unique=True, verbose_name='사업자등록번호')
    api_key = models.CharField(max_length=36, verbose_name='인증키')
    userid = models.CharField(max_length=256, verbose_name='파트너사 사용자 아이디')
    dev = models.BooleanField(default=False, null=False, verbose_name='테스트모드')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bank = BankHelper(self)


class BankAccount(models.Model):
    class Meta:
        verbose_name = '계좌'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['partner', 'bank', 'account_no'], name='unique_partner_bank_account'),
        ]

    partner = models.ForeignKey(Partner, null=False, blank=False, verbose_name='파트너', on_delete=models.PROTECT)
    collect_cycle = models.CharField(
        max_length=10, null=False, blank=False, choices=BankAccountCollectCycle.choices, verbose_name='수집주기'
    )
    bank = models.CharField(
        max_length=10, null=False, blank=False, choices=BankAccountBank.choices, verbose_name='은행'
    )
    account_type = models.CharField(
        max_length=1, null=False, blank=False, choices=BankAccountAccountType.choices, verbose_name='계좌유형'
    )
    account_no = models.CharField(
        max_length=50, null=False, blank=False, verbose_name='계좌번호'
    )
    alias = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='별칭')
    usage = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='용도')
    is_stop = models.BooleanField(default=False, null=False, verbose_name='해지')
    stop_date = models.DateField(null=True, blank=False, default=None, verbose_name='해지일')

    def update_bank_account(
            self,
            password: Optional[str] = None,
            web_id: Optional[str] = None,
            web_pwd: Optional[str] = None,
            identity_num: Optional[str] = None,
            alias: Optional[str] = None,
            usage: Optional[str] = None
    ):
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            BankAccountNum=self.account_no
        )
        if password:
            request_data['BankAccountPwd'] = password
        if web_id:
            request_data['WebId'] = web_id
        if web_pwd:
            request_data['WebPwd'] = web_pwd
        if identity_num:
            request_data['IdentityNum'] = identity_num
        if alias:
            request_data['Alias'] = alias
        if usage:
            request_data['Usage'] = usage
        result = self.partner.bank.client.service.UpdateBankAccount(**request_data)
        if result != 1:
            raise BarobillAPIError(result)
        save_fields = []
        if self.alias != alias and alias is not None:
            self.alias = alias
            save_fields.append('alias')
        if self.usage != usage and usage is not None:
            self.usage = usage
            save_fields.append('usage')
        if len(save_fields) != 0:
            self.save(update_fields=save_fields)

    def stop_bank_account(self):
        if self.is_stop is True:
            raise BarobillError(901)
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            BankAccountNum=self.account_no
        )
        result = self.partner.bank.client.service.StopBankAccount(**request_data)
        if result != 1:
            raise BarobillAPIError(result)
        self.is_stop = True
        self.stop_date = timezone.localdate()
        self.save(update_fields=['is_stop', 'stop_date'])

    def cancel_stop_bank(self):
        if self.is_stop is False:
            raise BarobillError(902)
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            BankAccountNum=self.account_no
        )
        result = self.partner.bank.client.service.CancelStopBankAccount(**request_data)
        if result != 1:
            raise BarobillAPIError(result)
        self.is_stop = False
        self.stop_date = None
        self.save(update_fields=['is_stop', 'stop_date'])

    def re_register_bank_account(self):
        if self.is_stop is False:
            raise BarobillError(902)
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            BankAccountNum=self.account_no
        )
        result = self.partner.bank.client.service.ReRegistBankAccount(**request_data)
        if result != 1:
            raise BarobillAPIError(result)
        self.is_stop = False
        self.stop_date = None
        self.save(update_fields=['is_stop', 'stop_date'])

    def __update_log(self, log_list):
        """
        BankAccountLogEx2 의 list 값을 거래 기록에 등록한다.
        :param log_list: [BankAccountLogEx2]
        :return:None
        """
        parsed_log_list = map(bank_account_log_parser, log_list)
        transactions = BankAccountTransaction.objects.bulk_create(
            [BankAccountTransaction(bank_account=self, **parsed_log) for parsed_log in parsed_log_list],
            ignore_conflicts=True
        )

    def update_date_log(self, date_string: str):
        """
        지정한 날짜의 로그를 불러와 데이터베이스에 저장한다.
        :param date_string: YYYYMMDD 형태의 한국 날짜 string
        :return: None
        """
        page = 1
        log_list = []
        while True:
            result = self.get_daily_log(date_string, page)
            log_list += [] if result.BankAccountLogList is None else result.BankAccountLogList.BankAccountLogEx2
            if result.MaxPageNum == page:
                break
            page += 1
        self.__update_log(log_list)

    def update_today_log(self):
        """
        오늘 거래 내역을 불러오고, 데이터베이스에 저장한다.
        :return: None
        """
        date_string = timezone.localdate().strftime('%Y%m%d')
        self.update_date_log(date_string)

    def update_yesterday_log(self):
        """
        어제의 거래 내역을 불러오고, 데이터베이스에 저장한다.
        :return: None
        """
        date_string = (timezone.localdate() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        self.update_date_log(date_string)

    def get_log(
            self,
            start_date: str,
            end_date: str,
            page: int,
            direction: int = 1,
            per_page: int = 100,
            order: int = 1
    ):
        """
        주어진 기간에 대한 거래 내역을  불러온다.
        https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#GetPeriodBankAccountLogEx2
        :param start_date: 한국시간 YYYYMMDD 형태의 조회 시작일 string.
        :param end_date: 한국시간 YYYYMMDD 형태의 조회 종료일 string.
        :param page: 조회할 페이지 수
        :param direction: 거래 유형. 1 전체, 2 입금, 3출금
        :param per_page: 페이지 당 결과 표시 수(최대 100개)
        :param order: 거래일시 정렬 순서. 1 오름차순, 2. 내림차순
        :return: barobill API 결과를 그대로 반환한다.(https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#PagedBankAccountLogEx2)
        """
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            ID=self.partner.userid,
            BankAccountNum=self.account_no,
            StartDate=start_date,
            EndDate=end_date,
            TransDirection=direction,
            CountPerPage=per_page,
            CurrentPage=page,
            OrderDirection=order  # 1 오름차순, 2 내림차순
        )
        result = self.partner.bank.client.service.GetPeriodBankAccountLogEx2(**request_data)
        if result.CurrentPage <= 0:
            raise BarobillAPIError(result.CurrentPage)
        return result

    def get_daily_log(
            self,
            base_date: str,
            page: int,
            direction: int = 1,
            per_page: int = 100,
            order: int = 1
    ):
        """
        주어진 일자의 거래 내역을 불러온다.
        https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#GetDailyBankAccountLogEx2
        :param base_date: 한국시간 YYYYMMDD 형태의 조회일 string.
        :param page: 조회할 페이지 수
        :param direction: 거래 유형. 1 전체, 2 입금, 3출금
        :param per_page: 페이지 당 결과 표시 수(최대 100개)
        :param order: 거래일시 정렬 순서. 1 오름차순, 2. 내림차순
        :return: barobill API 결과를 그대로 반환한다.(https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#PagedBankAccountLogEx2)
        """
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            ID=self.partner.userid,
            BankAccountNum=self.account_no,
            BaseDate=base_date,
            TransDirection=direction,
            CountPerPage=per_page,
            CurrentPage=page,
            OrderDirection=order  # 1 오름차순, 2 내림차순
        )
        result = self.partner.bank.client.service.GetDailyBankAccountLogEx2(**request_data)
        if result.CurrentPage <= 0:
            raise BarobillAPIError(result.CurrentPage)
        return result

    def get_monthly_log(
            self,
            base_month: str,
            page: int,
            direction: int = 1,
            per_page: int = 100,
            order: int = 1
    ):
        """
        주어진 일자의 거래 내역을 불러온다.
        https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#GetMonthlyBankAccountLogEx2
        :param base_month: 한국시간 YYYYMM 형태의 조회월 string.
        :param page: 조회할 페이지 수
        :param direction: 거래 유형. 1 전체, 2 입금, 3출금
        :param per_page: 페이지 당 결과 표시 수(최대 100개)
        :param order: 거래일시 정렬 순서. 1 오름차순, 2. 내림차순
        :return: barobill API 결과를 그대로 반환한다.(https://dev.barobill.co.kr/docs/references/%EA%B3%84%EC%A2%8C%EC%A1%B0%ED%9A%8C-API#PagedBankAccountLogEx2)
        """
        request_data = dict(
            CERTKEY=self.partner.api_key,
            CorpNum=self.partner.brn,
            ID=self.partner.userid,
            BankAccountNum=self.account_no,
            BaseMonth=base_month,
            TransDirection=direction,
            CountPerPage=per_page,
            CurrentPage=page,
            OrderDirection=order  # 1 오름차순, 2 내림차순
        )
        result = self.partner.bank.client.service.GetDailyBankAccountLogEx2(**request_data)
        if result.CurrentPage <= 0:
            raise BarobillAPIError(result.CurrentPage)
        return result


class BankAccountTransaction(models.Model):
    class Meta:
        verbose_name = '입출금 기록'
        verbose_name_plural = verbose_name
        unique_together = ('bank_account', 'trans_ref_key')
        ordering = ['-trans_dt', 'bank_account']

    bank_account = models.ForeignKey(BankAccount, null=False, blank=False, on_delete=models.PROTECT)
    trans_direction = models.CharField(max_length=1, null=False, blank=False, choices=BankAccountTransactionDirection.choices)
    deposit = models.BigIntegerField(null=True, blank=False, default=None)
    withdraw = models.BigIntegerField(null=True, blank=False, default=None)
    balance = models.BigIntegerField(null=False, blank=False, default=0)
    trans_dt = models.DateTimeField(null=False, blank=False)
    trans_type = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='입출금구분')
    trans_office = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='입출금취급점')
    trans_remark = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='입출금비고')
    mgt_remark_1 = models.CharField(max_length=50, null=True, blank=False, default=None, verbose_name='비고1')
    trans_ref_key = models.CharField(max_length=24, null=False, blank=False, verbose_name='입출금내역 키')
    memo = models.CharField(max_length=100, null=True, blank=False, default=None, verbose_name='입출금내역 키')
    meta = models.JSONField(null=True, blank=False, default=None, verbose_name='추가 정보')
