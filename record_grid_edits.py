import gspread
import time
from gis_functions import query_layer
from generate_access_token import generate_access_token
from convert_num_to_letters import convert_num_to_letters

def record_grid_edits(token, layer, gsheet, sheet_name):
    gsheets_vals = []
    layer_features = query_layer(token, layer, "1=1")
    if not layer_features['features']:
        return ({404: "No survey features found"}, 404)
    else:
        layer_features = layer_features['features']
    try:
        gc = gspread.service_account(filename = './config/tnc205-auto-upload-a97fe4207469.json')
        workbook = gc.open(gsheet)
        sh = workbook.worksheet(sheet_name)
    except Exception as e:
        return ({500: e}, 500)
    num_rows = len(sh.col_values(1))+1
    headers = sh.row_values(1)
    oid_list = sh.col_values(headers.index('Object ID')+1)
    edit_date_list = sh.col_values(headers.index('EpochEditDate')+1)
    oid_dict = {}
    if not (len(oid_list) == len(edit_date_list)):
        return "Error: Object ID and EditDate lists are not the same length"
    for i in range(1,len(oid_list)):
        if oid_list[i] in oid_dict:
            oid_dict[oid_list[i]].append(int(edit_date_list[i])-int(edit_date_list[i])%1000)
        else:
            oid_dict[oid_list[i]] = [int(edit_date_list[i])-int(edit_date_list[i])%1000]
    status = {
        -2: "Mowed",
        -1: "High Priority",
        0: "Untreated",
        1: "Partially Treated",
        2: "Fully Treated",
        3: "Needs Future Retreatment"
    }
    for feature in layer_features:
        attr = feature['attributes']
        geo = feature['geometry']

        if (str(attr['OBJECTID']) in oid_dict):
            if (attr['EditDate']-attr['EditDate']%1000) in oid_dict[str(attr['OBJECTID'])]:
                continue

        vals = []
        vals.append(attr['OBJECTID'])
        vals.append(attr['TILE_ID'])
        vals.append(status[attr['Status']])
        vals.append(time.ctime(attr['EditDate']/1000 - (7*3600))),
        vals.append(attr['Editor'])
        vals.append(attr['AREA_GEO'])
        vals.append(attr['EditDate'])
        vals.append(str(geo))
        gsheets_vals.append(vals)
    if gsheets_vals:
        sh.update(f"A{num_rows}:AA{num_rows+len(gsheets_vals)}", gsheets_vals)
    return (len(gsheets_vals))

def record_current_state(token, layer, gsheet, sheet_name):
    gsheets_vals = []
    layer_features = query_layer(token, layer, "1=1")
    if not layer_features['features']:
        return ({404: "No features found"}, 404)
    else:
        layer_features = layer_features['features']
    try:
        gc = gspread.service_account(filename = './config/tnc205-auto-upload-a97fe4207469.json')
        workbook = gc.open(gsheet)
        workbook.del_worksheet(workbook.worksheet(sheet_name))
        workbook.add_worksheet(sheet_name, len(layer_features) + 1, len(layer_features[0]['attributes']) + 1)
        sh = workbook.worksheet(sheet_name)
    except Exception as e:
        return ({500: e}, 500)
    num_rows = len(sh.col_values(1))+1
    gsheets_vals.append(['Object ID', 'Tile ID', 'Status', 'Edit Date', 'Editor', 'Acreage', 'EpochEditDate'])
    status = {
        -2: "Mowed",
        -1: "High Priority",
        0: "Untreated",
        1: "Partially Treated",
        2: "Fully Treated",
        3: "Needs Future Retreatment"
    }
    for feature in layer_features:
        attr = feature['attributes']
        geo = feature['geometry']

        vals = []
        vals.append(attr['OBJECTID'])
        vals.append(attr['TILE_ID'])
        vals.append(status[attr['Status']])
        vals.append(time.ctime(attr['EditDate']/1000 - (7*3600))),
        vals.append(attr['Editor'])
        vals.append(attr['AREA_GEO'])
        vals.append(attr['EditDate'])
        vals.append(str(geo))
        gsheets_vals.append(vals)
    if gsheets_vals:
        end_letters = convert_num_to_letters(len(gsheets_vals[0])+1)
        end_num = len(gsheets_vals)+1
        end_cell = end_letters+str(end_num)
        sh.update(f"A1:{end_cell}", gsheets_vals)
    return (len(gsheets_vals)-1)

def email_days_work(token, layer):
    layer_features = query_layer(token, layer, "1=1")
    if not layer_features['features']:
        return ({404: "No survey features found"}, 404)
    else:
        layer_features = layer_features['features']
    status = {
        -2: "Mowed",
        -1: "High Priority",
        0: "Untreated",
        1: "Partially Treated",
        2: "Fully Treated",
        3: "Needs Future Retreatment"
    }
    todays_progress = {
        -2: 0,
        -1: 0,
        0: 0,
        1: 0,
        2: 0,
        3: 0
    }
    weeks_progress = {
        -2: 0,
        -1: 0,
        0: 0,
        1: 0,
        2: 0,
        3: 0
    }
    current_status = {
        -2: 0,
        -1: 0,
        0: 0,
        1: 0,
        2: 0,
        3: 0
    }
    
    utc_epoch = time.time()
    utc_tuple = time.gmtime()
    pst_epoch = utc_epoch - (7*3600)
    pst_tuple = time.gmtime(utc_epoch-(3600*7))
    today = [pst_tuple[7],pst_tuple[0]]
    this_week = []
    for i in range(0,pst_tuple[6]+1):
        week_day = time.gmtime(pst_epoch - (86400 * i))
        this_week.append([week_day[7], week_day[0]])
    for feature in layer_features:
        attr = feature['attributes']
        geo = feature['geometry']
        editTime = time.gmtime(attr['EditDate']/1000 - (7*3600))
        if today == [editTime[7], editTime[0]]:
            todays_progress[attr['Status']] += attr['AREA_GEO']
        if today in this_week:
            weeks_progress[attr['Status']] += attr['AREA_GEO']
        current_status[attr['Status']] += attr['AREA_GEO']
    subject = f"TNC205 Work Update for {pst_tuple[1]}/{pst_tuple[2]}/{pst_tuple[0]}"
    body = f"""
Hello!

Today's ({pst_tuple[1]}/{pst_tuple[2]}/{pst_tuple[0]}) TNC205 progress is as follows:
"""
    add = ''
    for i in range(-2,4):
        if todays_progress[i] > 0:
            add += f"{status[i]}: {round(todays_progress[i], 1)} acres\n"
    if add == '':
        body += "No progress today\n"
    else:
        body += add + "\n"
    body += "This week's status is as follows:\n"
    add = ''
    for i in range(-2,4):
        if weeks_progress[i] > 0:
            add += f"{status[i]}: {round(weeks_progress[i], 1)} acres\n"
    if add == '':
        body += "No progress this week\n"
    else:
        body += add + "\n"
    
    body += f"""
The overall grid status at TNC205 is as follows:
{status[-2]}: {round(current_status[-2], 1)} acres
{status[-1]}: {round(current_status[-1], 1)} acres
{status[0]}: {round(current_status[0], 1)} acres
{status[1]}: {round(current_status[1], 1)} acres
{status[2]}: {round(current_status[2], 1)} acres
{status[3]}: {round(current_status[3], 1)} acres
\n
Thanks!
--------------------------------------------------------------
Beep boop, I'm a bot. If you notice any errors, please email tanner@example.com
"""
    return (subject, body)
