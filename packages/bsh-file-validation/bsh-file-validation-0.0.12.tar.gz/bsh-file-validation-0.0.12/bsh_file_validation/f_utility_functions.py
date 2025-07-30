import pandas
import os
import os.path
from datetime import datetime


class Dtbaseconnect:
    VOLUMES_PATH = "/Volumes/"
    SOURCE_SYSTEM_PLACEHOLDER = "{sourcesystem}"
    def __init__(
        self,
        dbasecon,
        sourceName,
        source_dl_layer,
        dest_dl_layer,
        FNT_ID,
        FileTemplate,
        job_run_id,
        HierarchyFlag,
        spark,
        IOTFlag,
    ):
        self.dbcon = dbasecon
        self.spark = spark
        self.con = self.dbcon.fn_get_connection()
        self.sourceName = sourceName
        self.source_dl_layer = source_dl_layer
        self.dest_dl_layer = dest_dl_layer
        self.FNT_ID = FNT_ID
        self.FileTemplate = FileTemplate
        self.job_run_id = job_run_id
        self.HierarchyFlag = HierarchyFlag
        print("UtilityFunctions File")
        
        self.IOTFlag = IOTFlag

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

   

    def cleanNullTerms(self, d):
        return {k: v for k, v in d.items() if v is not None}

    def func_get_paths(self):
        try:
            statement = f"""select * from T_MST_file_path fp inner join T_mst_dl_layer la on la.PK_Dl_Layer_Id=fp.fk_dl_layer_id  
where la.PK_Dl_Layer_Id = (select PK_Dl_Layer_Id from T_mst_DL_layer where Dl_Layer_Name='{self.source_dl_layer}') or la.PK_Dl_Layer_Id = (select PK_Dl_Layer_Id from T_mst_DL_layer where Dl_Layer_Name='{self.dest_dl_layer}')"""
            
            exec_statement = self.con.prepareCall(statement)
            exec_statement.execute()
            resultSet = exec_statement.getResultSet()
            vals1 = {}
            while resultSet.next():
                vals = {}
                vals["Landing"] = resultSet.getString("Landing_Path")
                vals["Success"] = resultSet.getString("Success_File_Path")
                vals["Error"] = resultSet.getString("Error_File_Path")
                vals["Suspense"] = resultSet.getString("Suspense_File_Path")
                
                nonnull = self.cleanNullTerms(vals)
                vals1.update(nonnull)
                print("paths:", vals1)
            path = {}
            for value in vals1.keys():
                if value == "Landing" and self.IOTFlag == "True":
                    partitionname, foldername = self.fn_iotfolder()

                    path[value] = (
                        f"{self.VOLUMES_PATH}"
                        + vals1[value].replace(self.SOURCE_SYSTEM_PLACEHOLDER, self.sourceName)
                        + "/"
                        + foldername
                        + "/"
                        + partitionname
                    )
                elif value != "Landing":
                    path[value] = (
                        f"{self.VOLUMES_PATH}"
                        + vals1[value].replace(self.SOURCE_SYSTEM_PLACEHOLDER, self.sourceName)
                        + "/"
                        + self.FileTemplate
                    )

                else:
                    path[value] = f"{self.VOLUMES_PATH}" + vals1[value].replace(
                        self.SOURCE_SYSTEM_PLACEHOLDER, self.sourceName
                    )
            return path
            exec_statement.close()
        except Exception as e:
            print(e)

    def fn_iotfolder(self):
        statement = f"""select IOT_partition_name,IOT_folder_name from T_mst_file_standard_Schema where IS_IOT='{self.IOTFlag}' and FNT_Id='{self.FNT_ID}'"""
        print(statement)
        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()
        print(resultSet)
        while resultSet.next():

            iot_partition_name = resultSet.getString("IOT_partition_name")
            iot_folder_name = resultSet.getString("IOT_folder_name")

            

        return iot_partition_name, iot_folder_name
        

    def fn_get_list_of_paths(self, path, start, end):

        dbutils = self.get_dbutils()
        lst_files = []

        def get_dir_content(ls_path):
            
            print("ls path is", ls_path)
            dir_paths = dbutils.fs.ls(ls_path)
            print("dir path is", dir_paths)
            subdir_paths = [
                get_dir_content(p.path)
                for p in dir_paths
                if p.isDir() and p.path != ls_path
            ]
            
            flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
            
            final_list = [
                p.path for p in dir_paths if not p.isDir()
            ] + flat_subdir_paths
            return final_list

        if start is None:
            lst_files.extend(get_dir_content(path))
            list_of_name_time = [
                {
                    "CreatedTime": datetime.fromtimestamp(
                        os.path.getctime("/" + str(f).replace(":", ""))
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "FileName": os.path.split(f)[1],
                    "FilePath": ("/" + str(f).replace(":", "")),
                }
                for f in lst_files
            ]
        else:
            time_range = pandas.date_range(start, end, freq="H")
            for val in time_range:
                day = str(val.day).zfill(2)
                month = str(val.month).zfill(2)
                year = str(val.year).zfill(4)
                hour = str(val.hour).zfill(2)
                
                print(f"{path}/{year}/{month}/{day}/{hour}")
                fullpath = f"{path}/{year}/{month}/{day}/{hour}"
                try:
                    lst_files.extend(get_dir_content(fullpath))
                    list_of_name_time = [
                        {
                            "CreatedTime": datetime.fromtimestamp(
                                os.path.getctime("/" + str(f).replace(":", ""))
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            "FileName": os.path.split(f)[1],
                            "FilePath": ("/" + str(f).replace(":", "")),
                        }
                        for f in lst_files
                    ]
                except Exception as e:
                    print(e)
                    pass
        return list_of_name_time

    def fn_put_datepartition(self):
        current_time = datetime.now()
        return f"/{str(current_time.year).zfill(4)}/{str(current_time.month).zfill(2)}/{str(current_time.day).zfill(2)}/{str(current_time.hour).zfill(2)}/"

    def fn_get_file_params(self, FNT_ID):
        statement = f"""select typ.file_type ,fnt.batch_size from t_META_file_standard_Schema fnt inner join T_mst_file_type typ on \
          fnt.fk_file_type_id=typ.pk_file_type_id  where FNT_ID='{FNT_ID}'"""

        exec_statement = self.con.prepareCall(statement)
        exec_statement.execute()
        resultSet = exec_statement.getResultSet()

        while resultSet.next():
            vals = {}
            vals["File_Type"] = resultSet.getString("File_Type")
            vals["Batch_Size"] = resultSet.getInt("Batch_Size")

            # Close connections
        exec_statement.close()
        return vals

    def fn_calculate_file_path(
        self, fnt_id, filename, validation_status, file_id, reqpath, srcpath
    ):
        """
        The function to calculate file paths

        Parameters:
            fnt_id: Filename template id.
            filename: Filename template.
            validation_status:Status of attribute validations.
            file_id: File Id.

        Returns:
            Returns source, destination and resulr path.
        """
        print("filename is ", filename)
        self.filename = filename
        self.srcpath = srcpath
        result = None
        print("validation status is", validation_status)
        if validation_status:
            result = "Success"
            path = "Success"
        elif not validation_status:
            result = "Error"
            path = "Error"
        if fnt_id == 0:
            result = "Suspense"
            path = "Suspense"
        
        destpath = reqpath[path]

        
        src, dest = self.fn_get_src_dest_path(
            self.srcpath, destpath, file_id, self.filename
        )
        return src[1:], dest, result

    def fn_get_src_dest_path(self, srcpath, destPath, file_id, filename):
        """
        The function to move files

        Parameters:
            destPath:Destination path.
            file_id:File Id.
        Returns:
            Returns source path, destination path.
        """
        source_path = srcpath

        
        hie_folder = self.fn_put_datepartition()
        print("hie_folder is", hie_folder)
        if self.HierarchyFlag == "True":
            print("path parts are", destPath, self.FileTemplate, hie_folder, filename)
            
            print("src", source_path)
            destinationpath = destPath + hie_folder + filename
            print("dest", destinationpath)
        else:
            
            destinationpath = destPath + hie_folder + filename

        print("src and dest are", source_path, destinationpath)
        
        return source_path, destinationpath
