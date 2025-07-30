import json
from typing import List,Dict,Union


class updatinglogs:
    """This is a class for updating logs in database"""

    def __init__(
        self,
        dbcon,
        sourceName,
        dest_dl_layer,
        FNT_ID,
        job_run_id,
        HierarchyFlag,
        FileTemplate,
        spark1,
    ):
        """The constructor for updatinglogs class

        Parameters:
           sourceName(string)  : source system name of file.
           source_dl_layer (string): source file path.
           dest_dl_layer(string):destination file path.
           suc_path(string):Success file path.
           err_path(string):Error file path.
           sus_path(string):Suspense file path.
           FNT_ID(string):Filename Template Id.
           job_run_id(string):Job Run Id.
           FileTemplate(string):Filename Template.
        """

        self.sourceName = sourceName
        self.fnt_attributes_master = {}

        self.dest_dl_layer = dest_dl_layer

        self.FNT_ID = FNT_ID
        self.job_run_id = job_run_id
        self.HierarchyFlag = HierarchyFlag
        self.FileTemplate = FileTemplate
        self.a = dbcon

        self.con = self.a.fn_get_connection()

    def fn_log_List_of_Files(self, Json_file_list: str) -> List[Dict[str, Union[str, int]]]:
        """
        The function to update T_file_info log

        Parameters:
            Json_file_list: list that contains json file of file info

        Returns:
            Returns result dict contains filename,fnt_id,file_id,file_path.
        """
        try:
            print("json file is", Json_file_list)
            final_json = json.dumps(Json_file_list)
            print("-------json", final_json)
            statement = f"""EXEC dbo.sp_insert_T_file_info @json = '{final_json}', @fntid='{self.FNT_ID}' , @jobid='{self.job_run_id}'"""
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            result_dict = []
            # print(resultSet)
            while resultSet.next():
                vals = {}
                vals["FileName"] = resultSet.getString("File_Name")
                vals["FK_FNT_Id"] = resultSet.getInt("FK_FNT_Id")
                vals["PK_file_id"] = resultSet.getInt("PK_File_Id")
                vals["FilePath"] = resultSet.getString("File_path")

                result_dict.append(vals)
            # Close connections
            exec_statement.close()
            # self.con.close()
            print("Result_dict is", result_dict)
            return result_dict
        except Exception as e:
            print(e)

    def fn_log_attribute_values(self, jsonip):
        """
        The function to update attribute values

        Parameters:
            jsonip= json input
            file_id(string)=File id

        """
        print("trying to log into table", jsonip)

        statement = (
            f"""EXEC dbo.sp_insert_T_file_attribute_details_new @json = '{jsonip}'"""
        )
        print("fn_log_attribute_values - statement", statement)
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)

        # Close connections
        exec_statement.close()
        # self.con.close()

    def fn_update_attribute_validation(self, jsonip):
        """
        The function to update attribute validation log

        Parameters:
            Json_ip: Json input

        """
        print("jsonis", jsonip)
        try:
            statement = f"""EXEC dbo.sp_update_file_attribute_validation_new @json = '{jsonip}'"""
            exec_statement = self.con.prepareCall(statement)
            res = exec_statement.execute()
            print(res)

            # Close connections
            exec_statement.close()
        # self.con.close()

        except Exception as e:
            print(e)

   

    def fn_update_filepickup_ts(self, end_date, FNT_ID):
        """
        The function to update delta logs

        Parameters:
           FNT_ID: File name template Id.
           end_date: End date.
        """
        statement = f"""EXEC [dbo].[sp_insert_filepickupts] @Job_Run_Id ='{self.job_run_id}',@end_date ='{end_date}', @FNT_ID='{FNT_ID}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)

        # Close connections
        exec_statement.close()
        # self.con.close()
