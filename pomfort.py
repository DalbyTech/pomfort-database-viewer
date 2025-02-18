import datetime as dt
import re
import os 

database_paths = list()

def friendly_title(input_string):
    """filter sql table name and return an easier to read name if there is a match, otherwise just return the input"""
    mapping = {
        "ACHANGE": "Change",
        "ATRANSACTION": "Transaction",
        "ATRANSACTIONSTRING": "Transaction String",
        "ZACTIVITYJOB": "Activity Job",
        "ZACTIVITYTASK": "Activity Task",
        "ZAUDIOTRACK": "Audio Track",
        "ZCAMERAINFO": "Camera Info",
        "ZCOPYJOBTEMPLATE": "Copy Job Template",
        "ZCUEPOINT": "Cue Point",
        "ZDESTINATIONPATH": "Destination Path",
        "ZDYNAMICMETADATA": "Dynamic Metadata",
        "ZFILERESOURCE": "File Resource",
        "ZFOLDER": "Folder",
        "ZGENERALCOPYOPTIONSBLOB": "General Copy Options Blob",
        "ZGRADE": "Grade",
        "ZGRADEBININFO": "Grade Bin Info",
        "ZGRADEINFO": "Grade Info",
        "ZGRADENODE": "Grade Node",
        "ZHASHINFO": "Hash Info",
        "ZLENSCORRECTIONDATA": "Lens Correction Data",
        "ZLOOKLIBRARYENTRY": "Look Library Entry",
        "ZLOOKUPTABLE": "Lookup Table",
        "ZMEDIABININFO": "Media Bin Info",
        "ZMETADATA": "Metadata",
        "ZMHLFILE": "MHL File",
        "ZMOVIESETTINGBININFO": "Movie Setting Bin Info",
        "ZPROCESSINGINFO": "Processing Info",
        "ZPRODUCTIONINFO": "Production Info",
        "ZPROJECTINFO": "Project Info",
        "ZREMOTERESOURCE": "Remote Resource",
        "ZRENDERCONFIGURATION": "Render Configuration",
        "ZRENDERPRESET": "Render Preset",
        "ZRESOURCEOWNER": "Resource Owner",
        "ZSMARTFOLDERINFO": "Smart Folder Info",
        "ZTIMECODERANGE": "Timecode Range",
        "ZTRANSCODINGSOURCEINFO": "Transcoding Source Info",
        "ZUSERINFO": "User Info",
        "ZVERSION": "Version",
        "ZVIDEOCLIPAUDIOSOURCE": "Video Clip Audio Source",
        "ZVOLUME": "Volume",
        "Z_11DESTINATIONPATHS": "11 Destination Paths",
        "Z_11RESOLVEDDESTINATIONPATHS": "11 Resolved Destination Paths",
        "Z_18SOURCERESOURCES": "18 Source Resources",
        "Z_18SOURCEVERSIONS": "18 Source Versions",
        "Z_1DESTINATIONVOLUMES": "1 Destination Volumes",
        "Z_1PREVIOUSJOBS": "1 Previous Jobs",
        "Z_1SOURCEVOLUMES": "1 Source Volumes",
        "Z_20VERIFYRESOURCES": "20 Verify Resources",
        "Z_23AVAILABLEDESTINATIONPATHS": "23 Available Destination Paths",
        "Z_23FIRSTRUNDESTINATIONPATHS": "23 First Run Destination Paths",
        "Z_23SECONDRUNDESTINATIONPATHS": "23 Second Run Destination Paths",
        "Z_25USEDASDELETEDRESOURCEPATHBYRELINKTASKS": "25 Used As Deleted Resource Path By Relink Tasks",
        "Z_25USEDASDESTINATIONBYOFFLOADJOB": "25 Used As Destination By Offload Job",
        "Z_3DESTINATIONPATHS": "3 Destination Paths",
        "Z_67USEDINRENDERJOBS": "67 Used In Render Jobs",
        "Z_67USEDINRENDERTASKS": "67 Used In Render Tasks",
        "Z_69SIDECARS": "69 Sidecars",
        "Z_METADATA": "Metadata",
        "Z_MODELCACHE": "Model Cache",
        "Z_PRIMARYKEY": "Primary Key"
    }
    return mapping.get(input_string, input_string)




class time:
    custom_epoch = dt.datetime(2001, 1, 1, 0, 0, 0)

    @staticmethod
    def today() -> dt.datetime:
        now = dt.datetime.now()
        return dt.datetime(now.year, now.month, now.day)    
    
    @staticmethod
    def yesterday() -> dt.datetime:
        now = dt.datetime.now()
        today = dt.datetime(now.year, now.month, now.day)
        return today - dt.timedelta(days=1)
    
    @staticmethod
    def days_ago(d:int=1) -> dt.datetime:
        now = dt.datetime.now()
        today = dt.datetime(now.year, now.month, now.day)
        return today - dt.timedelta(days=d-1)

    @staticmethod
    def time_now() -> dt.datetime:
        return dt.datetime.now()
    
    @staticmethod
    def convert_pomfort_time(value: float) -> dt.datetime:
        try              : return time.custom_epoch + dt.timedelta(seconds=value)  # return creation date
        except ValueError: return 0




def parse_ZSTATEIDENTIFIER(input:str) -> str:
    """eg: com.pomfort.workState.finishedUnsuccessfully -> Finished Unsuccessfully"""
    input_split = list(input.split("."))
    if len(input_split) == 4 and input_split[2] == 'workState':
        output =  ' '.join(re.findall('[A-Z][a-z]*|[a-z]+', input_split[3])).title()
        #print(self.name, input, '->', output)
        return output
    



def get_databases() -> list:
    """Return a list of all the databases in the directory"""
    psdb = list()
    home_path = os.path.expanduser("~")
    db_path = os.path.join(home_path, "Library/Application Support/Pomfort/OffloadManager/")
    
    for item in os.listdir(db_path):
        path = os.path.join(db_path, item)
        if os.path.isdir(path):
            for item in os.listdir(path):
                if item.endswith('.psdb'): psdb.append(os.path.join(path, item))

    return psdb

database_paths = get_databases()






if __name__ == '__main__':
    get_databases()