from .f_attribute_retriever import AttributeRetriever
from .f_db_reader import databasereaders


class Retrivelistattributes:

    def __init__(self, dbcon, FNT_ID, job_run_id):

        
        self.job_run_id = job_run_id
        self.fnt_attributes_master = {}
        self.FNT_ID = FNT_ID
        self.a = dbcon
        self.dbread = databasereaders(self.a, self.FNT_ID, self.job_run_id)
        # print("spark in retriveattributes")

    def fn_file_process_slave_get_attributes(self, file):

        fnt_id = file["FK_FNT_Id"]
        file_id = file["PK_file_id"]
        file_path = file["FilePath"]

        # print('fnt id is',fnt_id)
        if fnt_id not in self.fnt_attributes_master:
            # print('fnt not in ')
            self.fnt_attributes_master[fnt_id] = self.dbread.fn_get_list_of_attributes(
                fnt_id
            )
        return self.fn_retrieve_individual_files_Attributes(
            fnt_id, file_id, file_path, self.fnt_attributes_master[fnt_id]
        )

    def fn_retrieve_individual_files_Attributes(
        self, fnt_id, file_id, file_path, attributes
    ):
        print("inside fn", file_path, file_id, fnt_id)
        print("attributes are", attributes)
        ar = AttributeRetriever(file_path, attributes)
        values = ar.fn_getattributes()
        print("values are", values)
        return values
