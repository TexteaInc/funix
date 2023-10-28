# This example shows how to change display labels for arguments 

import funix

@funix.funix(
    title="BMI Calculator",
    description = "**Calculate** _your_ BMI", 
    argument_labels = {
        "weight": "Weight (kg)", 
        "height": "Height (m)"
    }
    show_source=True,
)
def BMI(weight: float, height: float) -> str:
    bmi = weight / (height**2)
    return f"## Your BMI is: \n ###{bmi:.2f}"