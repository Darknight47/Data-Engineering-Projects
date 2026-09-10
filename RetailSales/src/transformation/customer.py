def transform_customer(df):
    # 1. Clean and standardize the customer data
    if df.isEmpty():
        raise ValueError("Customer dataset is empty")  # Fixed: changed return to raise

    expected_columns = {"customer_Id", "DOB", "Gender", "city_code"}
    missing_columns = expected_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns in customer dataset: {missing_columns}")

    # 2. Check for null customer IDs
    null_customer_ids = df.filter(df['customer_Id'].isNull()).count()
    if null_customer_ids > 0:
        raise ValueError(f"Customer dataset contains {null_customer_ids} null customer IDs")

    # 3. Check for duplicates (Fixed: Removed {} and appended .count())
    duplicate_count = (
        df.groupby('customer_Id')
        .count()
        .filter("count > 1")
        .count()
    )

    if duplicate_count > 0:
        raise ValueError(f"Customer dataset contains {duplicate_count} duplicate customer IDs")

    # 4. Apply clean schema naming
    df = df.withColumnRenamed("customer_Id", "customer_id") \
           .withColumnRenamed("DOB", "date_of_birth") \
           .withColumnRenamed("Gender", "gender")
    
    return df