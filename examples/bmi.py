import funix

@funix.funix(
    description = "**Calculate** _your_ BMI", 
    argument_labels = {
        "weight": "Weight (kg)", 
        "height": "Height (m)"
    }
)
def BMI(weight: float, height: float) -> str:
    bmi = weight / (height**2)
    return f"Your BMI is: {bmi:.2f}"