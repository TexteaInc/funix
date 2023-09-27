from funix import funix, new_funix_type


@new_funix_type({"name": "password", "config": None})
class NewPassword(str):
    def check_safe(self) -> bool:
        if (
            len(self) > 12
            and any(char.isdigit() for char in self)
            and any(char.isalpha() for char in self)
            and any(char.isupper() for char in self)
            and any(char.islower() for char in self)
        ):
            return True
        return False


@funix(
    description="Check if your password is safe.",
)
def password_check(password: NewPassword) -> str:
    return "Nice!" if password.check_safe() else "Oops!"
