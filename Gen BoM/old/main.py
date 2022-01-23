from numpy import NaN
import pandas as pd


RADIO_BOM_PATH = "v297n.csv"
MPC_BOM_PATH = "maintenance_port_card_variant0.csv"

radio_bom_header = pd.read_csv(RADIO_BOM_PATH, nrows=6, dtype='string', header=None, sep=';', engine='python',)

radio_bom_parts = pd.read_csv(RADIO_BOM_PATH, skiprows=8, sep=';', engine='python', dtype='string', skipfooter=1, quoting=3, names=['Part Name','Ref Des','Var Status','Qty','PART_NUMBER','DESCRIPTION','MFG_PN','MANUFACTURER'])
print(radio_bom_parts)
mpc_bom = pd.read_csv(MPC_BOM_PATH, skiprows=8, skipfooter=1,
                      header=None, engine='python', dtype='string')

radio_bom_header.drop(radio_bom_header.filter(
    regex="Unnamed"), axis=1, inplace=True)

# sorting radio BoM by part suffix
print(radio_bom_parts['Part Name'][0])
DCDC_Cutout = (radio_bom_parts['Ref Des'].str[-4:].isin(['_DC0'])).values.tolist()

Dig_Cutout1 = (
    radio_bom_parts['Ref Des'].str[-3:].isin(['_CG'])).values.tolist()
Dig_Cutout2 = (
    radio_bom_parts['Ref Des'].str[-4:].isin(['_DC1'])).values.tolist()
Dig_Cutout3 = (
    radio_bom_parts['Ref Des'].str[-5:].isin(['_DIG0'])).values.tolist()

Dig_Cutout = []

for i in range(len(Dig_Cutout1)):
    Dig_Cutout.append(Dig_Cutout1[i] or Dig_Cutout2[i] or Dig_Cutout3[i])

# deleting temp lists
del Dig_Cutout1
del Dig_Cutout2
del Dig_Cutout3

# radio bom with columns identifying part source
bom_copy = (radio_bom_parts.copy(deep=False))
bom_copy.insert(len(bom_copy.columns), 'DCDC_Cutout', DCDC_Cutout)
bom_copy.insert(len(bom_copy.columns), 'Dig_Cutout', Dig_Cutout)

# making DCDC BoM based on made label
DCDC_bom = (bom_copy[bom_copy.DCDC_Cutout != False])
DCDC_bom = DCDC_bom.reset_index(drop=True)
del DCDC_bom['Dig_Cutout']
del DCDC_bom['DCDC_Cutout']


DCDC_bom['Qty'] = DCDC_bom['Qty'].astype(int)
qty_total = DCDC_bom['Qty'].sum()
total_df = pd.DataFrame([['Total', NaN, NaN, qty_total,
                        NaN, NaN, NaN, NaN, NaN]], columns=list(DCDC_bom.columns))
DCDC_bom = DCDC_bom.append(total_df, ignore_index=True)

DCDC_BoM_Titled = pd.concat([radio_bom_header, DCDC_bom], ignore_index=False, axis=1)
DCDC_BoM_Titled.to_csv('./Gen BoM/DCDC_BoM.csv', index=False)

# making Dig BoM based on made label
Dig_bom = (bom_copy[bom_copy.Dig_Cutout != False])
Dig_bom = Dig_bom.reset_index(drop=True)
del Dig_bom['Dig_Cutout']
del Dig_bom['DCDC_Cutout']


Dig_bom['Qty'] = Dig_bom['Qty'].astype(int)
qty_total = Dig_bom['Qty'].sum()
total_df = pd.DataFrame([['Total', NaN, NaN, qty_total,
                        NaN, NaN, NaN, NaN, NaN]], columns=list(Dig_bom.columns))
Dig_bom = Dig_bom.append(total_df, ignore_index=True)


Dig_BoM_Titled = pd.concat([radio_bom_header, Dig_bom], ignore_index=False, axis=1)
Dig_BoM_Titled.to_csv('./Gen BoM/Dig_BoM.csv', index=False)

print('BoM Produced!')