import msal


class DBconnection:
    def __init__(self, database, server, spark1):
        self.database = database
        self.server = server
        self.spark = spark1
        

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

    def fn_get_connection(self):
        dbutils = self.get_dbutils()
        # Set url & credentials
        # jdbc_url = 'jdbc:sqlserver://sql-fof-dev.database.windows.net:1433;databaseName=Fof_config-db'
        tenant_id = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SPN-TenantId")
        sp_client_id = dbutils.secrets.get(
            scope="fof-prd-scope", key="EDA-SPN-ClientId"
        )
        sp_client_secret = dbutils.secrets.get(
            scope="fof-prd-scope", key="EDA-SPN-ClientSecret"
        )
        url = f"jdbc:sqlserver://{self.server};databaseName={self.database}"
        # Write your SQL statement as a string
        # Generate an OAuth2 access token for service principal
        authority = f"https://login.windows.net/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            sp_client_id, sp_client_secret, authority
        )
        token_response = app.acquire_token_for_client(scopes=["https://database.windows.net/.default"])["access_token"]
        # Create a spark properties object and pass the access token
        properties = self.spark._sc._gateway.jvm.java.util.Properties()
        properties.setProperty("accessToken", token_response)

        # Fetch the driver manager from your spark context
        driver_manager = self.spark._sc._gateway.jvm.java.sql.DriverManager

        # Create a connection object and pass the properties object
        con = driver_manager.getConnection(url, properties)
        print(con)
        return con