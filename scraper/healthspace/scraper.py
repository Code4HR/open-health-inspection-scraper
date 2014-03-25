import scrapertools

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
            if city.string not in cityNames:
                print 'Adding ' + city.string
                cityNames.append(city.string)
                citiesFound.append({
                    'name': city.string,
                    'locality': locality.string,
                    'baseUrl': city['href'][:city['href'].find('Food-List-ByName')],
                    'establishmentUrl': city['href'].replace('Count=30', 'Count=10000')
                })

    return citiesFound

def getEstablishments(city):
    establishmentsFound = []

    establishmentList = scrapertools.getContent(BASE_URL + city['establishmentUrl'])
    establishments = establishmentList.find_all('tr')
    for establishment in establishments:
        details = establishment.find_all('td')
        if len(details) == 4 and details[0] is not None and details[0].a is not None:

            geo = scrapertools.getLatLng(scrapertools.getText(details[2]), city["name"])

            establishmentsFound.append({
                'name': scrapertools.getText(details[0]),
                'url': details[0].a['href'],
                'address': scrapertools.getText(details[2]),
                'city': city['name'],
                'locality': city['locality'],
                'geo': {'type': "Point", 'coordinates': [geo['lat'], geo['lng']]},
                'last_inspection_date': scrapertools.getText(details[3])
            })

            print establishmentsFound
            exit(0)
    return establishmentsFound

def getInspections(establishment, cityUrl):
    inspectionsFound = []
    
    establishmentDetails = scrapertools.getContent(BASE_URL + establishment['url'])
    inspections = establishmentDetails.find_all(text='Inspection Type')[0].find_parent('table').find_all('tr')
    
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
    violations = violations.find_all('tr')
    for violation in violations:
        details = violation.find_all('td')
        
        violationsFound.append({
            'code': scrapertools.getAllText(details[0]),
            'observations': scrapertools.getAllText(details[1])
        })
    return violationsFound

