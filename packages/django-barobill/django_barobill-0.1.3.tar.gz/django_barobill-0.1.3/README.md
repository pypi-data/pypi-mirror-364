# Django Barobill
바로빌 연동을 위한 reusable package

## 설치
아래 명령어로 패키지 설치한 후

```pip install django-barobill```

`django`의 `settings.py` 내 `INSTALLED_APPS`에 `django_barobill`을 추가합니다.

```shell
INSTALLED_APPS = [
    ...
    'django.contrib.staticfiles',
    'django_barobill'
]
```

마지막으로 마이그레이션을 수행하여 필요한 테이블을 생성합니다.

```shell
python manage.py migrate
```

## 구성
### 파트너
이 패키지는 기본적으로 여러개의 파트너사를 한 앱에서 관리할 수 있게 구성되어 있습니다.

파트너사는 `models.Partner`에 저장되며 신규 파트너를 아래와 같이 등록할 수 있습니다.

```python
from django_barobill.models import Partner
상세 학목은 메서드의 docstring 참고

partner = Partner.objects.register_partner(
    '회사명', '사업자등록번호', 'api key', 'userid', dev=False 
)
```

## 계좌조회
### 계좌조회 관련 client
아래와 같이 은행 계좌 조회와 관련된 client를 생성한다.

```python
from django_barobill.models import Partner

partner = Partner.objects.first()

bank_client = partner.bank.client
```
### 계좌 등록
생성된 client에서 아래와 같이 계좌를 생성한다.
상세 학목은 메서드의 docstring 참고

```python
bank_account = bank_client.register_bank_account(
    '수금계좌', BankAccountCollectCycle.MINUTE10, BankAccountBank.HANA,
    BankAccountAccountType.C, '21223451241', '1234'
)
```

### 계좌 거래내역

#### 조회만
아래와 같은 형태로 거래내역을 조회힌다. 응답은 barobill의 응답을 변경없이 반환한다.
자세한 내용은 각 메서드의 docstring 참고
```python
# 기간 조회
log_duration = bank_client.get_log('20240101', '20240105', 1)
# 특정일 조회
log_day = bank_client.get_daily_log('20240101', 1)
# 특정월 조회
log_month = bank_client.get_monthly_log('202401', 1)
```

#### 조회 및 데이터베이스 등록
조회 후 데이터베이스 등록 까지 진행
자세한 내용은 각 메서드의 docstring 참고
```python
# 특정일 조회 및 등록
log_day = bank_client.update_date_log('20240101')
# 오늘 조회 및 등록
log_today = bank_client.update_today_log()
# 어제 조회 및 등록
log_yesterday = bank_client.update_yesterday_log()
```