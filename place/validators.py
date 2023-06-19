import re

def score_validator(score):
    # 5 이하의 소숫점 한자리 숫자
    score_regex = r"^([0-5]{1}$|^[0-4]{1})(\.{1}\d{0,1})?$"
    
    if not re.search(score_regex, str(score)):
        return True
    return False