import gspread
import time
from gis_functions import query_layer

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
        sh = workbook.add_worksheet(sheet_name, len(layer_features) + 1, len(layer_features[0]['attributes']) + 1)
    except Exception as e:
        return ({500: e}, 500)
    num_rows = len(sh.col_values(1))+1
    headers = sh.row_values(1)

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
        vals.append((time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime(attr['EditDate']/1000 - (7*3600)))))
        vals.append(attr['Editor'])
        vals.append(attr['AREA_GEO'])
        vals.append(attr['EditDate'])
        vals.append(str(geo))
        gsheets_vals.append(vals)
    if gsheets_vals:
        sh.update(f"A{num_rows}:AA{num_rows+len(gsheets_vals)}", gsheets_vals)
    return (len(gsheets_vals))
