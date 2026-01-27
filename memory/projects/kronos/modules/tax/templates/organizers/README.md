# Tax Organizer Templates
# Kronos Tax Module

This directory contains tax organizer templates for different client situations.

## Available Templates

1. **w2_employee.json** - Standard W-2 employees
2. **self_employed.json** - 1099 contractors and freelancers  
3. **small_business.json** - Schedule C business owners
4. **rental_property.json** - Schedule E rental income
5. **investment_income.json** - Stocks, dividends, capital gains
6. **retirement.json** - Retirees (pension, SS, RMDs)
7. **first_time_filer.json** - New tax filers (simplified)
8. **multi_state.json** - Multiple state returns
9. **high_net_worth.json** - Complex returns

## Template Structure

Each template is a JSON file with:
- `metadata` - Template info (name, description, estimated time)
- `sections` - Array of organizer sections
- `documents` - Required document types

## Customization

Templates can be customized per practice:
1. Copy the template you want to modify
2. Edit sections/questions as needed
3. Update the `custom_templates/` directory
4. Reference by custom name in organizer creation
