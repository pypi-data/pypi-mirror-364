

class AttributeValidator:
    """This is a class for validating file attributes."""

    def __init__(self, dbcon, attributes, file_id, FNT_ID):
        """The constructor for AttributeValidator class

        Parameters:
           attributes : File attributes from sql table.
           file_id (string): File_id of the particular file.
        """
        # print("attribute Validator File")
        self.FNT_ID = FNT_ID
        self.attributes = attributes
        self.file_id = file_id
        self.a = dbcon
        self.format = self.a.fn_get_file_params(self.FNT_ID)["File_Type"]
        self.function_mapper = {
            "gt_0": self.fn_check_gt_0,
            "Within_domain": self.fn_check_within_domain,
            "within_5_days": self.fn_check_within_5_days,
            "(300,300)": self.fn_check_img_resolution,
            "modes": self.fn_check_imgclr_mode,
            "within_dim": self.fn_check_vd_dimension,
            "duration_gt_0": self.fn_check_vd_duration,
            "bit_gt_0": self.fn_check_vd_bitrate,
        }

    def fn_check_gt_0(self, value):
        """
        The function to check size of the file.

        Parameters:
            value(int): Size of the file.

        Returns:
            Returns Boolean value.
        """
        
        print("size is", value)
        return int(value) > 0

    def fn_check_within_domain(self, value):
        """
        The function to check file format.

        Parameters:
            value (string):format of the file.

        Returns:
            Boolean value.
        """
        print("selfformat", self.format)
        print("other is", value)
        domain = [
            ".csv",
            ".txt",
            ".json",
            ".xml",
            ".parquet",
            ".jpg",
            ".jpeg",
            ".png",
            ".tif",
            "mp4",
            "mp3",
            "avi",
        ]
        print(domain)
        return value == "." + self.format

    def fn_check_within_5_days(self, value):
        """
        The function to check file inserted within 5 days.

        Parameters:
            value(ComplexNumber): File inserted time.

        Returns:
            True - if file inserted within 5 days.
        """
        print(value)
        from datetime import datetime, timedelta

        time_between_insertion = datetime.now() - timedelta(days=5)
        print(time_between_insertion)
        return True

    def fn_check_img_resolution(self, value):
        print(value)
        print(type(value))
        value = value[1:len(value) - 1]
        x = list(map(int, value.split(",")))
        return tuple(x) >= (300, 300)

    def fn_check_imgclr_mode(self, value):
        print(value)
        mode = ["L", "RGBA", "HSB", "RGB", "CMYK", "Grey scale", "Bitmap"]
        if value in mode:
            return True
        else:
            return False

    def fn_check_vd_duration(self, value):
        print("video duration is", value)
        return int(value) > 0

    def fn_check_vd_bitrate(self, value):
        print("bitrate", value)
        return int(value) > 0

    def fn_check_vd_dimension(self, value):
        print("Frame dimension", value)
        value = value[1:len(value) - 1]
        x = list(map(int, value.split(",")))
        return tuple(x) > (1000, 1000)

    def fn_getattributesValidation(self):
        """
        The function to validate file attributes.

        Parameters:0

        Returns:
             check results and list of details
        """
        subresult = {}

        list_of_details = []
        for b1 in self.attributes:
            details = {}
            if b1["Validation_Needed"]:
                print(b1["Validation_Type"])
                print(b1["File_Attribute_Value"])
                res = self.function_mapper[b1["Validation_Type"]](
                    b1["File_Attribute_Value"]
                )
                subresult[b1["FK_File_Attribute_Id"]] = res
                details["FK_File_Attribute_Id"] = b1["FK_File_Attribute_Id"]
                details["File_id"] = self.file_id
                details["validation_status"] = res
                list_of_details.append(details)
        
        result = all(subresult.values())
        return result, list_of_details

