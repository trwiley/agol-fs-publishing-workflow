# --> publish_to_online.py <--
# Command line script that publishes a provided map to ArcGIS online. Allows for overwriting of a service as well. 
# Heavily adapted from https://github.com/Esri/developer-support/blob/master/python/arcpy-python/publish-fs-to-arcgis-online/create_publish_mxd_with_fgdb_layers_as_hosted_service.py

import arcpy
import os
import sys
import xml.dom.minidom as dom


def see_if_service_def_exists(service_def):
    try:
        os.remove(service_def)
        print('File removed and overwritten')
    except OSError:
        print('No SD exists, writing one now.')


def change_types(tag_types):
    for tag_type in tag_types:
        if tag_type.parentNode.tagName == 'SVCManifest':
            if tag_type.hasChildNodes():
                tag_type.firstChild.data = 'esriServiceDefinitionType_Replacement'


def change_states(tag_states):
    for tag_state in tag_states:
        if tag_state.parentNode.tagName == 'SVCManifest':
            if tag_state.hasChildNodes():
                tag_state.firstChild.data = 'esriSDState_Published'


def change_service_type(type_names):
    for type_name in type_names:
        if type_name.firstChild.data == 'MapServer':
            type_name.firstChild.data = 'FeatureServer'


def turn_off_caching(config_props):
    prop_array = config_props.firstChild
    prop_sets = prop_array.childNodes
    for prop_set in prop_sets:
        key_values = prop_set.childNodes
        for key_value in key_values:
            if key_value.tagName == 'Key':
                if key_value.firstChild.data == 'isCached':
                    key_value.nextSibling.firstChild.data = 'false'


def turn_on_feature_access(config_props):
    prop_array = config_props.firstChild
    prop_sets = prop_array.childNodes
    for propSet in prop_sets:
        key_values = propSet.childNodes
        for key_value in key_values:
            if key_value.tag_name == 'Key':
                if key_value.firstChild.data == 'WebCapabilities':
                    key_value.nextSibling.firstChild.data = 'Query,Create,Update,Delete,Uploads,Editing'


def write_new_draft(sd, xml):
    f = open(sd, 'w')
    xml.writexml(f)
    f.close()


def publish_hosted_feature_service(map_doc,
                                   service_name,
                                   initial_sd_draft,
                                   share_level,
                                   share_org,
                                   share_groups,
                                   sd,
                                   updated_sd_draft,
                                   summary,
                                   tags):

    see_if_service_def_exists(sd)

    try:
        arcpy.mapping.CreateMapSDDraft(map_doc,
                                       initial_sd_draft,
                                       service_name,
                                       'MY_HOSTED_SERVICES',
                                       summary=summary,
                                       tags=tags)

        # Read the contents of the original SDDraft into an xml parser
        sd_draft_xml = dom.parse(initial_sd_draft)

        change_types(sd_draft_xml.getElementsByTagName('Type'))
        change_states(sd_draft_xml.getElementsByTagName('State'))
        change_service_type(sd_draft_xml.getElementsByTagName('TypeName'))

        turn_off_caching(sd_draft_xml.getElementsByTagName('ConfigurationProperties')[0])
        turn_on_feature_access(sd_draft_xml.getElementsByTagName('Info'[0]))

        write_new_draft(updated_sd_draft, sd_draft_xml)

        analysis = arcpy.mapping.AnalyzeForSD(updated_sd_draft)

        if analysis['errors'] == {}:
            # Stage the service
            arcpy.StageService_server(updated_sd_draft, sd)

            # Upload the service. The OVERRIDE_DEFINITION parameter allows you to override the
            # sharing properties set in the service definition with new values.
            arcpy.UploadServiceDefinition_server(in_sd_file=sd,
                                                 in_server='My Hosted Services',
                                                 in_service_name=service_name,
                                                 in_override='OVERRIDE_DEFINITION',
                                                 in_my_contents='SHARE_ONLINE',
                                                 in_public=share_level,
                                                 in_organization=share_org,
                                                 in_groups=share_groups)

            print 'Uploaded and overwrote service.'

        else:
            # If the sd draft analysis contained errors, display them and quit.
            print analysis['errors']
    except:
        print arcpy.GetMessages()


def main():

    user_path = sys.argv[1]
    map_doc = arcpy.mapping.MapDocument(sys.argv[2])
    sd_draft = sys.argv[3]
    updated_sd = sys.argv[4]
    service_name = sys.argv[5]
    sd = sys.argv[6]

    summary = sys.argv[7]
    tags = sys.argv[8]

    share_level = sys.argv[9]
    share_org = sys.argv[10]
    share_groups = sys.argv[11]

    arcpy.mapping.CreateMapSDDraft(map_document=user_path + map_doc,
                                   out_sddraft=user_path + sd_draft,
                                   service_name=service_name,
                                   server_type='MY_HOSTED_SERVICES',
                                   summary=summary,
                                   tags=tags)

    publish_hosted_feature_service(user_path + map_doc,
                                   service_name,
                                   user_path + sd_draft,
                                   share_level,
                                   share_org,
                                   share_groups,
                                   user_path + sd,
                                   updated_sd,
                                   summary,
                                   tags)


main()
