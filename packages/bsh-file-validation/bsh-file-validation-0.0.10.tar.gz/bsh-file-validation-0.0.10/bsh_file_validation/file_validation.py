import uuid
import json
# import multiprocessing as mp
from datetime import datetime
from pyspark.sql import SparkSession

from .f_attribute_validator import AttributeValidator as avr
from .f_utility_functions import Dtbaseconnect as dbcon1
from .f_retrive_listoffiles import RetriveListofFiles as rlf
from .f_log_files import updatinglogs as ul
from .f_db_reader import databasereaders as dbr
from .f_retrive_listofattributes import Retrivelistattributes as ra
from .f_database_connect import DBconnection as db
from .f_logs import commonlogs as cl
from . import get_sparkutils


class FileValidation:

    def __init__(self, SourceSystem, HierarchyFlag, IOTFlag, FNT_ID, FileTemplate) -> None:
        self.SourceSystem = SourceSystem
        self.HierarchyFlag = HierarchyFlag
        self.IOTFlag = IOTFlag
        self.FNT_ID = FNT_ID
        self.FileTemplate = FileTemplate

    def fn_process_files(self, batchfiles, cmnlogs, job_run_id, pipeline_run_id, source_dl_layer, dbcon, fv_flag, dbasecon, updlogs, path):
        batchlen = len(batchfiles)
        print("batchfiles are------------ ", batchfiles)
        print("in step 1 inserting delta logs for", batchlen, "files")
        cmnlogs.fn_insert_delta_logs(
            batchfiles, job_run_id, pipeline_run_id, from_dl_layer=source_dl_layer
        )
        print("in step 2 get file attribute list")
        ratt = ra(dbcon, self.FNT_ID, job_run_id)
        file_attribute_list = []
        res_list = []
        if fv_flag == 0:
            overall_res = True
            for file in batchfiles:
                res = {}
                sourcepath, destinationpath, result = dbasecon.fn_calculate_file_path(
                    file["FK_FNT_Id"],
                    file["FileName"],
                    overall_res,
                    file["PK_file_id"],
                    path,
                    file["FilePath"],
                )
                res["File_val_res"] = overall_res
                res["File_Name"] = file["FileName"]
                res["sourcepath"] = sourcepath
                res["destinationpath"] = destinationpath
                res["File_id"] = file["PK_file_id"]
                res["result"] = result
                res_list.append(res)
            cmnlogs.fn_update_delta_logs_new(
                batchfiles,
                job_run_id,
                to_dl_layer=None,
                to_dl_layer_path=None,
                validation_status="completed",
            )
        else:
            for file in batchfiles:
                file_attributes = ratt.fn_file_process_slave_get_attributes(file)
                print("file_attributes", file_attributes)
                # print('i:',type(i))
                length_file_att = len(file_attributes)
                len_file_att = length_file_att - 1
                while len_file_att > -1:
                    file_attributes[len_file_att]["PK_file_id"] = file["PK_file_id"]
                    len_file_att = len_file_att - 1
                file_attribute_list.append(file_attributes)

            print("list of file attributes:", file_attribute_list)
            print("in step 3 updating attribute details log")
            updlogs.fn_log_attribute_values(json.dumps(file_attribute_list))
            res_list = []
            detailed_list = []
            for file_att, file in zip(file_attribute_list, batchfiles):
                res = {"File_val_res": "", "File_Name": ""}
                print("file_att---- ", file_att)
                print("file----- ", file)
                av = avr(dbasecon, file_att, file["PK_file_id"], self.FNT_ID)
                print("file_att-------", file_att)
                overall_res, detailed_res = av.fn_getattributesValidation()
                print("overall_res-----------------", overall_res)
                print("detailed_res--------------", detailed_res)
                detailed_list.append(detailed_res)
                print("details status resis", detailed_list)

                sourcepath, destinationpath, result = dbasecon.fn_calculate_file_path(
                    file["FK_FNT_Id"],
                    file["FileName"],
                    overall_res,
                    file["PK_file_id"],
                    path,
                    file["FilePath"],
                )
                print("sorcepath ", sourcepath)
                print("destinationpath ", destinationpath)
                res["File_val_res"] = overall_res
                res["File_Name"] = file["FileName"]
                res["sourcepath"] = sourcepath
                res["destinationpath"] = destinationpath
                res["File_id"] = file["PK_file_id"]
                res["result"] = result
                res_list.append(res)
            print("result is---------------- ", res_list)
            print("detailed_list-----", detailed_list)
            cmnlogs.fn_update_delta_logs_new(
                batchfiles,
                job_run_id,
                to_dl_layer=None,
                to_dl_layer_path=None,
                validation_status="completed",
            )
            updlogs.fn_update_attribute_validation(json.dumps(detailed_list))
        return res_list

    def fn_copyfiles(self, batchfiles, cmnlogs, job_run_id, dest_dl_layer, dbutils):
        file1 = {}
        for file in batchfiles:
            filename = file["File_Name"]
            sourcepath = file["sourcepath"]
            destinationpath = file["destinationpath"]
            file_id = file["File_id"]
            result = file["result"]
            
            actual_src_path = sourcepath.replace('Volumes/','/Volumes/')
            # actual_destpath = destinationpath if destinationpath.startswith("dbfs:") else destinationpath
            actual_destpath = destinationpath
            
            print("source and destination paths are ", actual_src_path, actual_destpath)
            
            if result == "Error":
                cmnlogs.fn_add_alerts(
                    self.FNT_ID,
                    "File_Validation_Error",
                    " " + str(filename),
                    job_run_id + "-" + self.FNT_ID,
                    file_id,
                )
            
            # Moving file from landing to bronze
            dbutils.fs.mv(actual_src_path, actual_destpath, recurse=True)  # noqa: F821
            
            file1[file_id] = "processed"
        
        # Updating delta logs after moving file to bronze layer
        cmnlogs.fn_update_delta_logs_newcopy(
            batchfiles,
            job_run_id,
            to_dl_layer=dest_dl_layer,
            copy_activity_status="completed",
        )
        return file1

    def validate(self):
        job_run_id=str(uuid.uuid4())
        print(job_run_id)
        pipeline_run_id=str(uuid.uuid4())
        # SourceSystem='Persondetails'
        # HierarchyFlag='False'
        # IOTFlag='False'
        # FNT_ID='96'
        # FileTemplate='T_person_data'

        spark1 = SparkSession.builder.appName("integrity-tests").getOrCreate()

        utils = get_sparkutils.getsparkutils(spark1)
        dbutils = utils.dbutils

        # creates an instance of the class
        sqlserver = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-ServerName")  # noqa: F821
        sqldatabase = dbutils.secrets.get(scope="fof-prd-scope", key="EDA-SQLDB-DBName")  # noqa: F821

        dest_dl_layer = "Bronze"
        source_dl_layer = "Landing"
        success_path = "success"
        error_path = "error"
        suspense_path = "suspense"

        # object for utility function
        dbcon = db(sqldatabase, sqlserver, spark1)
        dbasecon = dbcon1(
            dbasecon=dbcon,
            sourceName=self.SourceSystem,
            source_dl_layer=source_dl_layer,
            dest_dl_layer=dest_dl_layer,
            FNT_ID=self.FNT_ID,
            FileTemplate=self.FileTemplate,
            job_run_id=job_run_id,
            HierarchyFlag=self.HierarchyFlag,
            spark=spark1,
            IOTFlag=self.IOTFlag,
        )

        path = dbasecon.func_get_paths()
        success_destpath = path["Success"]
        print("succdestpath---", success_destpath)
        error_destpath = path["Error"]
        if dest_dl_layer == "Bronze":
            suspense_destpath = path["Suspense"]

        # object creation for retrivelistoffiles
        rtfiles = rlf(
            dbasecon,
            dbcon,
            sourceName=self.SourceSystem,
            source_dl_layer=source_dl_layer,
            dest_dl_layer=dest_dl_layer,
            HierarchyFlag=self.HierarchyFlag,
            FNT_ID=self.FNT_ID,
            FileTemplate=self.FileTemplate,
            job_run_id=job_run_id,
            spark1=spark1,
        )

        # object for
        updlogs = ul(
            dbcon,
            sourceName=self.SourceSystem,
            dest_dl_layer=dest_dl_layer,
            FNT_ID=self.FNT_ID,
            job_run_id=job_run_id,
            HierarchyFlag=self.HierarchyFlag,
            FileTemplate=self.FileTemplate,
            spark1=spark1,
        )

        # retrieve the list if files in landing
        cmnlogs = cl(
            dbcon,
            sourceName=self.SourceSystem,
            dest_dl_layer=dest_dl_layer,
            key="FileValidation",
            FNT_ID=self.FNT_ID,
            job_run_id=job_run_id,
            HierarchyFlag=self.HierarchyFlag,
            FileTemplate=self.FileTemplate,
            spark1=spark1,
        )
        end_date = datetime.now().strftime("%Y-%m-%d %H:00:00")
        print("end_date", end_date)

        lst = rtfiles.fn_Retrieve_list_of_files(end_date)
        print("Final list is ", lst)
        # final_lst=lst.replace("[[","[").replace("]]","]").replace("[],","").replace(",[]","")
        # log the list of files in db
        landingtimelogs = dbr(dbcon, self.FNT_ID, job_run_id)
        list_of_fnts = updlogs.fn_log_List_of_Files(lst)
        print("list of fnts", list_of_fnts)
        print("Length of list_fnts", len(list_of_fnts))

        if len(list_of_fnts) > 0:
            pk_file_id = list_of_fnts[0]["PK_file_id"]
            print(pk_file_id)
            Arrival_time = landingtimelogs.fn_get_landing_time(pk_file_id)
            expected_landingtime = landingtimelogs.fn_get_file_schema_details()
            fv_flag = expected_landingtime[0]["FV_Needed"]
            print(Arrival_time)
            print(expected_landingtime)
            # # Late arriving file
            # if int(Arrival_time[0]["TimeDiffinSeconds"]) > int(
            #     expected_landingtime[0]["Incoming_freqvalue"]
            # ):
            #     # alert
            #     delay = int(Arrival_time[0]["TimeDiffinSeconds"]) - int(
            #         expected_landingtime[0]["Incoming_freqvalue"]
            #     )
            #     cmnlogs.fn_add_alerts(
            #         FNT_ID,
            #         "FILE_LANDED_LATE",
            #         " The file was delayed by " + str(delay) + " seconds",
            #         job_run_id + "-" + FNT_ID,
            #         pk_file_id,
            #     )
            #     print("alertsent")

        # manager = mp.Manager()
        # return_dict = manager.dict()
        # n_cores = 2
        # attributes_all = {}
        # procs = []
        # final_list_of_results = {}

        # move files in batches
        batchsize = dbasecon.fn_get_file_params(self.FNT_ID)["Batch_Size"]
        print("bs--", batchsize)

        if batchsize == 0:
            batchsize = 10
        for value in range(0, len(list_of_fnts), batchsize):
            index1 = value
            print("index1", index1)
            opt = self.fn_process_files(
                list_of_fnts[index1: index1 + batchsize], cmnlogs, job_run_id, pipeline_run_id,
                source_dl_layer=source_dl_layer, dbcon=dbcon, fv_flag=fv_flag, dbasecon=dbasecon, updlogs=updlogs, path=path)
            updation_status = self.fn_copyfiles(
                opt, cmnlogs=cmnlogs, job_run_id=job_run_id, dest_dl_layer=dest_dl_layer, dbutils=dbutils)

        if self.HierarchyFlag == "True":
            updlogs.fn_update_filepickup_ts(end_date, self.FNT_ID)
            print("Timestamp updated for lastpickup field")