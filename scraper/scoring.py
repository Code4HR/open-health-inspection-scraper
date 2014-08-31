import config
import mongolab


'''
Weights for calculating the total vendor score.
The integer indicates how many inspections to use in the score and the
decimals are the weights for each inspection in descending order by date
'''
weights = {3: [0.6, 0.3, 0.1],
           2: [0.7, 0.3],
           1: [1.0]}

# The min and max range for the score
score_range = [0, 100]

# The per inspection scoring. The system is additive.
scoring = {'base': -2.0,
           'critical': -1.5,
           'repeat': -1.5,
           'corrected': 0.5}

c = config.load()
db = mongolab.connect()
va_establishments = db[c['state_abb']]

vendors = va_establishments.find({}, {'inspections': 1, '_id': 1})

for vendor in vendors:

    inspection_scores = []

    for inspection in vendor['inspections']:
        score = score_range[1]  # Set score to max

        # These are the actual calculations for the per inspection score. Modify here to use
        # different criteria
        for violation in inspection['violations']:
            score += scoring['base']
            if violation['critical']:
                score += scoring['critical']
            if violation['repeat']:
                score += scoring['repeat']
            if violation['corrected']:
                score += scoring['corrected']

        score = max(score, score_range[0])  # Make sure score does not go below min

        inspection_scores.append([inspection['date'], score])

        # Update each inspection in DB with score
        va_establishments.update({'_id': vendor['_id'],
                                  'inspections.date': inspection['date']},
                                 {'$set': {'inspections.$.score': score}},
                                 False,
                                 False)
    # Set the correct weight to use based on number of inspections the vendor has
    num_inspections = min(max(weights), len(inspection_scores))

    if num_inspections > 0:
        current_weights = weights[num_inspections]
        vendor_score = score_range[0]

        for i, inspection in enumerate(sorted(inspection_scores, reverse=True)):
            if i < num_inspections:
                vendor_score += inspection[1]*current_weights[i]

        va_establishments.update({'_id': vendor['_id']},
                                 {'$set': {'score': vendor_score}},
                                 False,
                                 False)

        print 'Record ' + str(vendor['_id']) + ' scored ' + str(vendor_score)