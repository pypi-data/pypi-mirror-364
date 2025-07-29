def validate_non_empty(value,name):
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
    return value.strip()

def validate_int(value,name):
    try:
        return int(value)
    except:
        raise ValueError(f"{name} must be numeric")

def validate_email(email):
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")
    return email.strip()

    