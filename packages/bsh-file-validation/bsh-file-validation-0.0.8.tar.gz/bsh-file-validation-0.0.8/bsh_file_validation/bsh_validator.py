

def read_csv_from_blob(spark, storage_account, container, blob_name, sas_token):
    url = f"wasbs://{container}@{storage_account}.blob.core.windows.net/{blob_name}?{sas_token}"
    df = spark.read.format("csv") \
        .option("header", "true") \
        .load(url)
    return df


def validate_columns(df, required_columns):
    actual_columns = df.columns
    missing = [col for col in required_columns if col not in actual_columns]
    if missing:
        print(f"❌ Validation failed. Missing columns: {missing}")
        return False
    else:
        print("✅ Validation passed. All required columns are present.")
        return True


def validate_no_nulls(df, critical_columns):
    for col in critical_columns:
        null_count = df.filter(df[col].isNull() | (df[col] == '')).count()
        if null_count > 0:
            print(f"❌ Validation failed. Column '{col}' has {null_count} null or empty values.")
            return False
    print("✅ Validation passed. No nulls in critical columns.")
    return True


def write_csv_to_blob(df, storage_account, container, blob_name, sas_token):
    url = f"wasbs://{container}@{storage_account}.blob.core.windows.net/{blob_name}"
    df.write.format("csv") \
        .option("header", "true") \
        .mode("overwrite") \
        .save(url + "?" + sas_token)
    print(f"✅ File successfully written to: {container}/{blob_name}")