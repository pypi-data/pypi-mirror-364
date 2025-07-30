from django.db import models

class BankAccountCollectCycle(models.TextChoices):
    MINUTE10 = 'MINUTE10', '10분'
    MINUTE30 = 'MINUTE30', '30분'
    HOUR1 = 'HOUR1', '1시간'
    HOUR4 = 'HOUR4', '4시간'
    DAY1 = 'DAY1', '1일'

class BankAccountBank(models.TextChoices):
    KB = 'KB', '국민은행'
    SHINHAN = 'SHINHAN', '신한은행'
    NH = 'NH', '농협은행'
    HANA = 'HANA', '하나은행'
    SC = 'SC', '제일은행'
    WOORI = 'WOORI', '우리은행'
    IBK = 'IBK', '기업은행'
    KDB = 'KDB', '산업은행'
    KFCC = 'KFCC', '새마을금고'
    CITI = 'CITI', '씨티은행'
    SUHYUP = 'SUHYUP', '수협은행'
    CU = 'CU', '신협은행'
    EPOST = 'EPOST', '우체국'
    KJBANK = 'KJBANK', '광주은행'
    JBBANK = 'JBBANK', '전북은행'
    DGB = 'DGB', '대구은행'
    BUSANBANK = 'BUSANBANK', '부산은행'
    KNBANK = 'KNBANK', '경남은행'
    EJEJUBANK = 'EJEJUBANK', '제주은행'
    KBANK = 'KBANK', '케이뱅크'

class BankAccountAccountType(models.TextChoices):
    C = 'C', '법인계좌'
    P = 'P', '개인계좌'

class BankAccountTransactionDirection(models.TextChoices):
    Deposit = 'D', '입금'
    Withdraw = 'W', '출금'
    ETC = 'E', '기타'