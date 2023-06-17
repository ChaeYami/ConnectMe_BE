import re

def password_validator(password):
    # 8자 이상의 영문 대소문자와 숫자, 특수문자 포함
    password_regex = '^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$'
    
    if not re.search(password_regex, str(password)):
        return True
    return False

# def password_pattern(password):
#     # 3자이상 같은 문자가 연속할 경우 불가
#     password_pattern = r"(.)\1+\1"
    
#     if re.search(password_pattern, str(password)):
#         return True
#     return False

def phone_validator(phone):
    # 11자 숫자
    phone_validations = r"^[0-9]{10,11}$"
    if re.search(phone_validations, str(phone)):
        return True
    return False
    
def account_validator(account):
    # 5자 이상 20자 이하 숫자 / 영문 대소문자
    account_validations = r"^[A-Za-z0-9]{5,20}$"
    
    if not re.search(account_validations, str(account)):
        return True
    return False


def nickname_validator(nickname):
    # 2자 이상 8자 이하의 영문 대소문자, 한글 / 특수문자는 _와 -만 허용
    nickname_validation = r"^[가-힣ㄱ-ㅎa-zA-Z0-9._-]{2,8}$"
    
    
    if not re.search(nickname_validation, str(nickname)):
        return True
    return False