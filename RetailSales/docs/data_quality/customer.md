### Customer — Data Quality Rules

#### customer_id
- Must not be null
- Must be unique
- Expected type: integer

#### date_of_birth
- Must be a valid date
- Null values are allowed
- Source column: DOB

#### gender
- Must contain an accepted value or null
- Values should be standardized

#### city_code
- Expected numeric/integer type
- Null values are allowed

#### Duplicate handling
- Duplicate customer_id records are treated as a DQ failure
- Do not silently drop duplicates