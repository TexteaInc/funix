from funix import funix, new_funix_type
import ipywidgets


@new_funix_type(
    widget={
        "name": "password", 
        "config": None
    }
)
# class NewPassword(ipywidgets.Password):
class NewPassword(str):
    def check_safe(self) -> bool:
        if (
            # len(self.value) > 6
            # and any(char.isdigit() for char in self.value)
            # and any(char.isupper() for char in self.value)
            # and any(char.islower() for char in self.value)
            len(self) > 6
            and any(char.isdigit() for char in self)
            and any(char.isupper() for char in self)
            and any(char.islower() for char in self)
        ):
            return True
        return False


@funix(
    title="New data type", 
    description="""
    
# Defining your own data type and associating a widget with it 

In this example, using Python's native class definition syntax, we first define a new data type `NewPassword` inherited from the Python's standard `str` type. It has a member function `check_safe` which checks if the password is strong.

Then, we use the `new_funix_type` decorator to associate the `NewPassword` type with the `password` widget. So a string of the `NewPassword` type will not be displayed as a normal string, but hidden when being entered. 

Now you can try it below. 
""",
    show_source=True,
)
def password_check(password: NewPassword="Freedom!1") -> str:
    safe_message = "Your password is strong."
    warning_message = "Your password is weak. It needs to contain at least 6 characters, including at least one digit, one upper case letter, and one lower case letter."

    return safe_message if password.check_safe() else warning_message
