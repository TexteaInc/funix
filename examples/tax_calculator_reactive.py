from funix import funix

@funix(disable=True)
def compute_tax(salary: float, income_tax_rate: float) -> int:
    return salary * income_tax_rate


@funix(    
    reactive={"tax": compute_tax}
    )
def after_tax_income_calculator(
    salary: float, 
    income_tax_rate: float, 
    tax: float) -> str:
    return f"Your take home money is {salary - tax} dollars,\
    for a salary of {salary} dollars, \
    after a {income_tax_rate*100}% income tax."
