def is_valid_username(username: str) -> bool:
    """بررسی معتبر بودن نام کاربری"""
    return username and len(username) >= 3 and username.isalnum()

def is_valid_password(password: str) -> bool:
    """بررسی معتبر بودن رمز عبور"""
    return password and len(password) >= 3