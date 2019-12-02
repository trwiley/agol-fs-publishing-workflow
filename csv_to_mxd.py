import arcpy
import sys

target_geodatabase = sys.argv[1]
target_csv = sys.argv[2]
target_map = sys.argv[3]
table_name = sys.argv[4]

arcpy.env.workspace = target_geodatabase
arcpy.TableToTable_conversion(target_csv, target_geodatabase, table_name)

map = arcpy.mapping.MapDocument(target_map)

map_data_frame = arcpy.mapping.ListDataFrames(map)

table_view = arcpy.mapping.TableView(target_geodatabase + '\\' + table_name)

arcpy.mapping.AddTableView(map_data_frame[0], table_view)

map.save()
