import json


class commonlogs:
    def __init__(
        self,
        dbcon,
        sourceName,
        dest_dl_layer,
        key,
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
        self.key = key
        self.sourceName = sourceName
        self.fnt_attributes_master = {}
       

        self.dest_dl_layer = dest_dl_layer

        self.FNT_ID = FNT_ID
        self.job_run_id = job_run_id
        self.HierarchyFlag = HierarchyFlag
        self.FileTemplate = FileTemplate
        self.a = dbcon

        self.con = self.a.fn_get_connection()

    def fn_insert_delta_logs(
        self, file, job_id, pipeline_run_id, from_dl_layer, ref_tracking_ids=None
    ):
        """
        The function to insert T_file_delta logs

        Parameters:
            file_id: File Id.
            job_id: Job run Id.
            pipeline_run_id: Pipeline run Id.
            fnt_id: Filename Template Id.
            from_dl_layer: From delta layer.
            from_dl_layer_path: From delta layer path.
            ref_tracking_ids: Reference tracking Id.

        """
        print("inset logs functions")
        print("in func", file)
        print(self.key)
        statement = f"""EXEC dbo.[sp_insert_T_file_deltas_new] @json = '{json.dumps(file)}' ,@job_run_id ='{job_id}',@pipeline_run_id ='{pipeline_run_id}',@from_dl_layer ='{from_dl_layer}',@key='{self.key}',@ref_tracking_ids='{ref_tracking_ids}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        exec_statement.close()

    def fn_update_delta_logs_new(
        self,
        file,
        job_id,
        to_dl_layer,
        to_dl_layer_path,
        validation_status=None,
        copy_activity_status=None,
        validation_result=None,
        ref_tracking_ids=None,
    ):
        """
        The function to update delta logs

        Parameters:
            file_id: File Id.
            job_id: Job run Id.
            fnt_id: Filename Template Id.
            to_dl_layer: To delta layer.
            to_dl_layer_path: To delta layer path.
            validation_status
            copy_activity_status
            validation_result
            ref_tracking_ids: Reference tracking Id.


        Returns:
            Returns result dict contains filename,fnt_id,file_id,file_path.
        """

        statement = f"""EXEC dbo.[sp_update_log_T_file_deltas_dqf_validation] @tracking_id ='{job_id+'-'+str(self.FNT_ID)}',@json = '{json.dumps(file)}',@to_dl_layer ='{to_dl_layer}',@to_dl_layer_path ='{to_dl_layer_path}',@validation_status ='{validation_status}',@copy_Activity_status ='{copy_activity_status}',@validation_result={validation_result},@key='{self.key}',@ref_tracking_ids='{ref_tracking_ids}'"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print("error-----", res)
        # Close connections
        exec_statement.close()
        # self.con.close()

    def fn_update_delta_logs_newcopy(
        self,
        file,
        job_id,
        to_dl_layer,
        validation_status=None,
        copy_activity_status=None,
        ref_tracking_ids=None,
    ):

        statement = f"""EXEC dbo.[sp_update_log_T_file_deltas_file_validation] @tracking_id ='{job_id+'-'+str(self.FNT_ID)}',@json='{json.dumps(file)}',@to_dl_layer ='{to_dl_layer}',@validation_status ='{validation_status}',@copy_Activity_status ='{copy_activity_status}',@key='{self.key}',@ref_tracking_ids={ref_tracking_ids}"""
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        exec_statement.close()

    def fn_add_alerts(self, fnt_id, alert_type, remarks, tracking_id, file_id):
        """
        The function to add alerts

        Parameters:

            fnt_id: Filename Template Id.
            alert_type: Type of alerts.
            remarks: remarks for alert


        """

        print("trying to insert  to alerts")
        print("alert type", alert_type)
        print("fnt_id", fnt_id)
        print("remarks", remarks)
        statement = f"""EXEC dbo.[sp_alert_Handler] @Alert_validation_Type ='{alert_type}',@FilenameTemplate_id ='{fnt_id}',@remarks='{remarks}',@tracking_id='{tracking_id}',@FK_File_id='{file_id}'"""
        print("Statement is ", statement)
        exec_statement = self.con.prepareCall(statement)
        res = exec_statement.execute()
        print(res)
        exec_statement.close()