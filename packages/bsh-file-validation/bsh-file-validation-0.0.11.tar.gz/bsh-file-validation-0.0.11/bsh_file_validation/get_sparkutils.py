class getsparkutils:
    def __init__(self, spark):
        self.spark = spark
        self.dbutils = self.get_db_utils()

    def get_db_utils(self):
        dbutils = None
        if self.spark.conf.get("spark.databricks.service.client.enabled") == "true":

            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)

        else:

            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]

        return dbutils


class abc:
    def nav(self, a):
        self.a = a
        return a + 6
