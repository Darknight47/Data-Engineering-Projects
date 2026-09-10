def transform_customer(df):
    # clean and standardize the customer data
    if(df.isEmpty()):
        return ValueError("Customer dataset is empty")

    expected_columns = {"customer_Id", "DOB", "Gender", "city_code"}

    missing_columns = expected_columns - set(df.columns)

    if(missing_columns):
        raise ValueError(f"Missing columns in customer dataset: {missing_columns}")

    null_customer_ids = df.filter(
        df['customer_Id'].isNull()
    ).count()

    if(null_customer_ids > 0):
        raise ValueError(f"Customer dataset contains {null_customer_ids} null customer IDs")

    duplicate_customer_ids = {
        df.groupby('customer_Id')
        .count()
        .filter("count > 1")
    }

    if(duplicate_customer_ids > 0):
        raise ValueError(f"Customer dataset contains duplicate customer IDs: {duplicate_customer_ids}")

    df = df.withColumnRenamed("customer_Id", "customer_id") \
       .withColumnRenamed("DOB", "date_of_birth") \
       .withColumnRenamed("Gender", "gender")
    
    return df