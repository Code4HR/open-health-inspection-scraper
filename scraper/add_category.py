import config
import mongolab
from pymongo import errors

c = config.load()

db = mongolab.connect()
va_establishments = db[c['state_abb']]

categories = {'Seasonal Fast Food Restaurant': 'Restaurant',
              'Fast Food Restaurant': 'Restaurant',
              'Full Service Restaurant': 'Restaurant',
              'Public Middle or High School Food Service': 'Education',
              'Mobile Food Unit': 'Mobile Food',
              'Private Elementary School Food Service': 'Education',
              'Child Care Food Service': 'Education',
              'Other Food Service': 'Other',
              'Mobile food unit': 'Mobile Food',
              'Public Elementary School Food Service': 'Education',
              'Dept. of Juvenile Justice Food Service': 'Government',
              'Carry Out Food Service Only': 'Grocery',
              'Commissary': 'Grocery',
              'Hotel Continental Breakfast': 'Hospitality',
              'Full Service Restaurant/Caterer': 'Restaurant',
              'Hospital Food Service': 'Medical',
              'Caterer': 'Restaurant',
              'State College Food Service': 'Education',
              'Convenience Store Food Service': 'Grocery',
              'Private Middle or High School Food Service': 'Education',
              'Bed & Breakfast Food Service': 'Hospitality',
              'Adult Care Home Food Service': 'Medical',
              'Fast Food Restaurant/Caterer': 'Restaurant',
              'Adult Day Care Food Service': 'Medical',
              'Nursing Home Food Service': 'Medical',
              'Summer Food Service Program Feeding Site': 'Education',
              'Jail Food Service': 'Government',
              'Private College Food Service': 'Education',
              'Group Home Food Service': 'Medical',
              'Seasonal Full Service Restaurant': 'Restaurant',
              'Summer Camp Food Service': 'Education',
              'Grocery Store Food Service': 'Grocery',
              'Public Elementry School Food Service': 'Education',
              'Public Primary School Food Service': 'Education',
              'Private High School Food Service': 'Education',
              'State Institution Food Service': 'Government',
              'Summer camp kitchen': 'Education',
              'Institution': 'Government',
              'Residential Child Care Institution Food Service': 'Education',
              'Summer Food Service Program Kitchen': 'Education',
              'Hotel continental breakfast': 'Hospitality',
              'Public school kitchen': 'Education',
              'Snack Bar': 'Grocery',
              'Bed & Breakfast': 'Hospitality',
              'Restaurant': 'Restaurant',
              'Private Elementry School Food Service': 'Education',
              'Adult care home food service': 'Medical'}


for vendor_type in categories:
    try:
        va_establishments.update({'type': vendor_type},
            {'$set': {'category': categories[vendor_type]}},
            multi=True)
        print vendor_type + ": " + categories[vendor_type] + ', update successful'
    except errors.OperationFailure:
        print vendor_type + ": " + categories[vendor_type] + ', update failed'
