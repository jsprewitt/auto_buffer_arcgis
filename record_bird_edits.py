import gspread
import time
from gis_functions import query_layer

def record_bird_edits(token, layer, gsheet, sheet_name):
    gsheets_vals = []
    survey_features = query_layer(token, layer, "1=1")
    if not survey_features['features']:
        return ({404: "No survey features found"}, 404)
    else:
        survey_features = survey_features['features']
    try:
        gc = gspread.service_account(filename = './config/tnc205-auto-upload-a97fe4207469.json')
        sh = gc.open(gsheet).worksheet(sheet_name)
    except Exception as e:
        return ({500: e}, 500)
    num_rows = len(sh.col_values(1))+1
    headers = sh.row_values(1)
    oid_list = sh.col_values(headers.index('Nest ID')+1)
    edit_date_list = sh.col_values(headers.index('EpochEditDate')+1)
    oid_dict = {}
    if not (len(oid_list) == len(edit_date_list)):
        return "Error: Object ID and EditDate lists are not the same length"
    for i in range(1,len(oid_list)):
        if oid_list[i] in oid_dict:
            oid_dict[oid_list[i]].append(int(edit_date_list[i])-int(edit_date_list[i])%1000)
        else:
            oid_dict[oid_list[i]] = [int(edit_date_list[i])-int(edit_date_list[i])%1000]

    for feature in survey_features:
        attr = feature['attributes']
        geo = feature['geometry']

        if (str(attr['objectid']) in oid_dict):
            if (attr['EditDate']-attr['EditDate']%1000) in oid_dict[str(attr['objectid'])]:
                continue
        
        species = attr['species']
        if species == "other":
            species = attr['species_other']
        
        nest_status = attr['nest_status']
        if nest_status == 'other':
            nest_status = attr['nest_status_other']
        
        nest_activity = attr['nest_activity']
        if nest_activity == 'other':
            nest_activity = attr['nest_activity_other']

        vals = []
        vals.append(attr['objectid'])
        vals.append(attr['nest_id'])
        vals.append(species)
        vals.append(attr['buffer_ft'])
        vals.append(nest_status)
        vals.append(nest_activity)
        vals.append(attr['eggs'])
        vals.append(attr['chicks'])
        vals.append(attr['fenced_or_marked'])
        try:
            vals.append(time.strftime('%m/%d/%Y %H:%M', time.gmtime(attr['anticipated_fledge_date']/1000 - (7*3600))))
        except:
            vals.append(attr['anticipated_fledge_date'])
        try:
            vals.append(time.strftime('%m/%d/%Y %H:%M', time.gmtime(attr['observation_date']/1000 - (7*3600))))
        except:
            vals.append(attr['observation_date'])
        vals.append(attr['project_area'])
        vals.append(attr['weather_conditions'])
        vals.append(attr['nest_description'])
        vals.append(attr['biologists_obervations']) # note the typo in ob/s/ervations...)
        vals.append(attr['disturbance_notes'])
        vals.append(attr['device_id'])
        vals.append(geo['y'])
        vals.append(geo['x'])
        vals.append(attr['accuracy'])
        vals.append(time.strftime('%m/%d/%Y %H:%M', time.gmtime(attr['CreationDate']/1000 - (7*3600))))
        vals.append(time.strftime('%m/%d/%Y %H:%M', time.gmtime(attr['EditDate']/1000 - (7*3600))))
        vals.append(attr['CreationDate'])
        vals.append(attr['EditDate'])
        vals.append(attr['Creator'])
        vals.append(attr['Editor'])
        gsheets_vals.append(vals)
    
    if gsheets_vals:
        sh.update(f"A{num_rows}:AA{num_rows+len(gsheets_vals)}", gsheets_vals)
    return len(gsheets_vals)
