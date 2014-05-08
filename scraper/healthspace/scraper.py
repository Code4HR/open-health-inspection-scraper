import scrapertools
import re

BASE_URL = 'http://www.healthspace.com/'
LOCALITY_LIST_URL = 'Clients/VDH/vdh_website.nsf/Main-HealthRegions?OpenView&Count=10000'
CITY_LIST_URL = '/Food-CityList'

def getCities():
    citiesFound = []
    cityNames = []
    
    localityList = scrapertools.getContent(BASE_URL + LOCALITY_LIST_URL)
    localities = localityList.body.div.img.find_all_next('a')

    for locality in localities:
        cityList = scrapertools.getContent(BASE_URL + locality['href'] + CITY_LIST_URL)
        cities = cityList.find_all('a')
        
        for city in cities:
            name = str(city.string).strip()
            if name not in cityNames:
                print 'Adding ' + name
                cityNames.append(name)
                citiesFound.append({
                    'name': name,
                    'locality': str(locality.string).strip(),
                    'baseUrl': city['href'][:city['href'].find('Food-List-ByName')],
                    'establishmentUrl': city['href'].replace('Count=30', '')
                })

    return citiesFound

def getEstablishments(city):
    establishmentsFound = []

    start = 1
    count = 1000
    more = True

    while more:
        establishmentList = scrapertools.getContent(BASE_URL + city['establishmentUrl']+'&start='+str(start)+'&count='+str(count))
        if establishmentList.find(text='No documents found') is not None:
            more = False
            continue
        start += count
        establishments = establishmentList.find_all('tr')
        for establishment in establishments:
            details = establishment.find_all('td')
            if len(details) == 4 and details[0] is not None and details[0].a is not None:
                establishmentsFound.append({
                    'name': scrapertools.getText(details[0]),
                    'url': details[0].a['href'],
                    'address': scrapertools.getText(details[2]),
                    'locality': city['locality'],
                    'last_inspection_date': scrapertools.getText(details[3])
                })

    return establishmentsFound


def getEstablishmentDetails(establishment):
    establishmentDetails = scrapertools.getContent(BASE_URL + establishment['url'])
    establishment['city'] =  re.sub('(<(/)?br>)|(\r)|(\n)',
                                    '',
                                    str(establishmentDetails.find(text=re.compile("Facility Location")).parent.next_sibling.find('br')))
    geo = scrapertools.getLatLng(establishment['address'], establishment['city'])
    if geo is not None:
        establishment['geo'] = {'type': 'Point', 'coordinates': [geo['lng'], geo['lat']]}
    establishment['type'] = establishmentDetails.find(text=re.compile("Facility Type")).parent.next_sibling.string

    return establishment


def getInspections(establishment, cityUrl):
    inspectionsFound = []
    
    establishmentDetails = scrapertools.getContent(BASE_URL + establishment['url'])
    inspections = establishmentDetails.find_all(text='Inspection Type')[0].find_parent('tr').find_all_next('tr')

    for inspection in inspections:
        details = inspection.find_all('td')

        if(details[0].a is None):
            continue
        
        violations = getViolations(BASE_URL + cityUrl + '/' + details[0].a['href'])
        inspectionsFound.append({
            'type': scrapertools.getText(details[0]),
            'date': scrapertools.getText(details[1]),
            'violations': violations
        })
    
    return inspectionsFound

def getViolations(inspectionDetailsUrl):
    violationsFound = []
    
    inspectionDetails = scrapertools.getContent(inspectionDetailsUrl)

    violations = inspectionDetails.find(text='Violations:').find_next('table')

    if violations is None:
        return []
    violations = violations.find('tr').find_next_siblings()
    for violation in violations:
        details = violation.find_all('td')

        violationsFound.append({
            'code': scrapertools.getAllText(details[0])[0],
            'repeat': any(['Repeat' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'critical': any(['Critical' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'corrected': any(['Corrected' in tag.string for tag in details[1].contents if tag.name == 'b']),
            'correction': ' '.join([tag.string for tag in details[1].contents if tag.name == 'font']).strip(),
            'observation': ' '.join([tag.string for tag in details[1].contents if tag.name == None]).strip()
        })
    return violationsFound

