import os
from PIL import Image
from datetime import datetime
import pathlib
from tinytag import TinyTag
from moviepy.editor import VideoFileClip


class AttributeRetriever:
    """This is the class to Retrive the attributes."""

    def __init__(self, file_path, attributes):
       
        # print("Attribute Retriver File")
        print("attributes are ", attributes)
        self.file_path = file_path
        self.attributes = [a["File_Attribute_Name"] for a in attributes]
        self.datatypes = {
            a["File_Attribute_Name"]: a["Value_DataType"] for a in attributes
        }
        self.all_attributes = attributes
        # print(self.datatypes)
        self.path = "/" + str(file_path).replace(":", "")
        self.function_mapper = {
            "size": self.fn_getSize,
            "createdtime": self.fn_get_createdTime,
            "modifiedtime": self.fn_get_modifiedTime,
            "filetype": self.fn_getType,
            "imgresolution": self.fn_img_resolution,
            "imgclrmode": self.fn_img_colormode,
            "videoduration": self.fn_video_duration,
            "videobitrate": self.fn_video_bit_rate,
            "videodimension": self.fn_video_frame_dimension,
        }

    def fn_get_createdTime(self):
        """
        function : fn_get_createdTime
        Description : This Function return the file created time
        parameters : 0
        returns : file created time
        return type : Datatime
        """
        print("path is", self.path)
        print(os.path.getctime(self.path))
        return datetime.fromtimestamp(os.path.getctime(self.path)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def fn_get_modifiedTime(self):
        """
        function : fn_get_modifiedTime
        Description : This Function return the file last modified time
        parameters : 0
        returns : file last modified time
        return type : Datatime
        """
        return datetime.fromtimestamp(os.path.getmtime(self.path)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def fn_getPath(self):
        """
        function : fn_getPath
        Description : This Function return the file path
        parameters : 0
        returns : file Path
        return type : string
        """
        return os.path.abspath(self.path)

    def fn_getType(self):
        """
        function : fn_getType
        Description : This Function return the fileType
        parameters : 0
        returns : fileType
        return type : string
        """
    
        print("path is", self.path)
        if pathlib.Path(self.path).is_dir():
            lst = list(
                set(
                    [
                        pathlib.Path(a).suffix
                        for a in pathlib.Path(self.path).iterdir()
                        if pathlib.Path(a).suffix != ""
                    ]
                )
            )
            if len(lst) > 0:
                file_format = lst[0]
            else:
                file_format = None
            print("***file format is", file_format)
            return file_format
        else:
            return pathlib.Path(self.path).suffix

    def fn_getSize(self):
        """
        function : fn_getSize
        Description : This Function return the file size
        parameters : 0
        returns : filesize
        return type : int
        """
        print("size 1 is", os.path.getsize(self.path))
        return os.path.getsize(self.path)

    def fn_img_resolution(self):
        with open(self.path, "rb") as f:
            image = Image.open(f)
        return str(image.size)

    def fn_img_colormode(self):
        with open(self.path, "rb") as f:
            image = Image.open(f)
        return image.mode

    def fn_video_duration(self):
        try:
            video = VideoFileClip(self.path)
            return int(video.duration)
        except Exception as e:
            print(e)
            return 0

    def fn_video_bit_rate(self):
        video = TinyTag.get(self.path)
        return int(video.bitrate)

    def fn_video_frame_dimension(self):
        video = VideoFileClip(self.path)
        return str(video.size)

    def fn_getattributes(self):
        list_of_values = []
        # print('attributes are',self.all_attributes)
        """
        function : fn_getattributes
        Description : This Function return the list of values that contains attribute name,value,
                  Datatype,Mapping_Id,attribute_Id,validation_needed,validation_type
        parameters : 0
        returns : list will all attribute details
        return type : list
        """
        for a in self.all_attributes:
            if a["File_Attribute_Name"] in self.function_mapper.keys():
                values = {}
                print("retrieivng ", a["File_Attribute_Name"])
                values["File_Attribute_Name"] = a["File_Attribute_Name"]
                values["File_Attribute_Value"] = self.function_mapper[
                    a["File_Attribute_Name"]
                ]()
    
                values["Value_DataType"] = a["Value_DataType"]
                values["FNT_File_Attribute_Mapping_Id"] = a[
                    "FNT_File_Attribute_Mapping_Id"
                ]
                values["FK_File_Attribute_Id"] = a["FK_File_Attribute_Id"]
                values["Validation_Needed"] = a["Validation_Needed"]
                values["Validation_Type"] = a["Validation_Type"]
                list_of_values.append(values)
            # print('value is',values)
            else:
                print(f"Attribute {a['File_Attribute_Name']} not found in function_mapper.")
        # print('value ===',list_of_values)
        return list_of_values
