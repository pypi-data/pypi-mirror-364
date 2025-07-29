# from pyspark.sql import SparkSession
# from F_AttributeRetriever import AttributeRetriever

class databasereaders:

    def __init__(self, dbcon, FNT_ID, job_run_id):
        self.job_run_id = job_run_id
        print("RetriveListOfFIles file")
        self.FNT_ID = FNT_ID
        self.a = dbcon
        self.con = self.a.fn_get_connection()

    def fn_get_hierarchypath(self, end_date, rootpath):
        statement = f"""exec [dbo].[sp_get_filepickuptime] @fntid='{self.FNT_ID}'"""
        print(statement)
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        results = []
        while resultSet.next():
            vals = {}
            vals["date_string"] = resultSet.getString("LastFilePickup_Ts")
            results.append(vals)
            sdate = results[0]
            start_date = list(sdate.values())[0]
            print("Start_date is ", start_date)
            lst_json = self.a.fn_get_list_of_paths(rootpath, start_date, end_date)
            print("lst_json", lst_json)
        return lst_json

    def fn_get_list_of_attributes(self, fnt_id: int):
        try:
            statement = f"""EXEC dbo.sp_get_mapped_attributes @fnt_id = {fnt_id}"""

            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            result_dict = []
            while resultSet.next():
                vals = {}
                vals["File_Attribute_Name"] = resultSet.getString("File_Attribute_Name")
                vals["Validation_Needed"] = resultSet.getBoolean("Validtion_Needed")
                vals["Validation_Type"] = resultSet.getString("Validation_Type")
                vals["Value_DataType"] = resultSet.getString("Value_DataType")
                vals["FNT_File_Attribute_Mapping_Id"] = resultSet.getString(
                    "FNT_File_Attribute_Mapping_Id"
                )
                vals["FK_File_Attribute_Id"] = resultSet.getString(
                    "FK_File_Attribute_Id"
                )

                result_dict.append(vals)

            # Close connections
            exec_statement.close()
            # self.con.close()
            return result_dict
        except Exception as e:
            print(e)

    def fn_get_landing_time(self, pk_file_id):
        statement = (
            f"""exec [dbo].[sp_get_Late_Arriving_Files] @file_id='{pk_file_id}'"""
        )
        print(statement)
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        results = []
        while resultSet.next():
            vals = {}
            vals["Landing_Time"] = resultSet.getString("Landing_Time")
            vals["Pk_file_id"] = resultSet.getString("Pk_file_id")
            vals["TimeDiffinSeconds"] = resultSet.getString("TimeDiffinSeconds")
            results.append(vals)

        return results

    def fn_get_file_schema_details(self):
        statement = f"""select Incoming_freqvalue, FK_Incoming_frequnit,FV_Needed from T_META_File_Standard_Schema where fnt_id='{self.FNT_ID}'"""
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        results = []
        while resultSet.next():
            vals = {}
            vals["FK_Incoming_frequnit"] = resultSet.getString("FK_Incoming_frequnit")
            if vals["FK_Incoming_frequnit"] == "min":
                vals["Incoming_freqvalue"] = resultSet.getInt("Incoming_freqvalue")
                vals["Incoming_freqvalue"] = vals["Incoming_freqvalue"] * 60
            elif vals["FK_Incoming_frequnit"] == "hr":
                vals["Incoming_freqvalue"] = resultSet.getInt("Incoming_freqvalue")
                vals["Incoming_freqvalue"] = vals["Incoming_freqvalue"] * 60 * 60
            else:
                vals["Incoming_freqvalue"] = resultSet.getInt("Incoming_freqvalue")
                
            vals["FV_Needed"] = resultSet.getInt("FV_Needed")
            results.append(vals)
        return results
