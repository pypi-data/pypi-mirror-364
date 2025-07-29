from .f_db_reader import databasereaders
import os
from datetime import datetime


class RetriveListofFiles:

    def __init__(
        self,
        dbcon,
        con,
        sourceName,
        source_dl_layer,
        dest_dl_layer,
        HierarchyFlag,
        FNT_ID,
        FileTemplate,
        job_run_id,
        spark1,
    ):
        
        self.spark = spark1
        dbutils = self.get_dbutils()
        print(dbutils)
        self.job_run_id = job_run_id
        
        self.sourceName = sourceName
        self.source_dl_layer = source_dl_layer
        self.dest_dl_layer = dest_dl_layer
        self.HierarchyFlag = HierarchyFlag
        self.FNT_ID = FNT_ID
        self.FileTemplate = FileTemplate
        self.a = dbcon
        self.con = con
        self.dbread = databasereaders(self.con, self.FNT_ID, self.job_run_id)
        

    def get_dbutils(self):
        try:
            from pyspark.dbutils import DBUtils

            dbutils = DBUtils(self.spark)
        except ImportError:
            import IPython

            dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils

    def fn_Retrieve_list_of_files(self, end_date) -> list:

        try:

            
           
            path = self.a.func_get_paths()
            rootpath = path[self.source_dl_layer]
            self.end_date = end_date
            print("File_listing_path", rootpath)
            print(self.end_date)
            print("hierarchy")
            if self.HierarchyFlag == "True":
                listofjson = self.fn_Retrive_list_of_files_hierarchy0(
                    self.end_date, rootpath
                )
                return listofjson
            else:
                listofnametime = self.fn_Retrieve_list_of_files_hierarchy1(rootpath)
                return listofnametime
        except Exception as e:
            print(e)
            return list()

    def fn_Retrive_list_of_files_hierarchy0(self, endate, rootpath):
        self.end_date = endate
        self.rootpath = rootpath
        list_json = self.dbread.fn_get_hierarchypath(self.end_date, self.rootpath)
        return list_json

    def fn_Retrieve_list_of_files_hierarchy1(self, rootpath):
        dbutils = self.get_dbutils()
        print("root path is", rootpath)
        print("executing dbutils comand")
        fileList = dbutils.fs.ls(rootpath)
        print("done executing dbutils comand")
        print("filelist is", fileList)
        print("file template is", self.FileTemplate)
        listoffiles = []
        for files in fileList:
            if files.name.startswith(self.FileTemplate):
                
                listoffiles.append(
                    [
                        files.path.replace("dbfs:", ""),
                        files.name,
                        files.size,
                        files.modificationTime,
                    ]
                )
                
        list_of_name_time = [
            {
                "CreatedTime": datetime.fromtimestamp(
                    os.path.getctime("/" + str(f[0]).replace(":", ""))
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "FileName": f[1],
                "FilePath": (str(f[0]).replace(":", "")),
            }
            for f in listoffiles
        ]
        print("lst with time and path", list_of_name_time)
        return list_of_name_time
