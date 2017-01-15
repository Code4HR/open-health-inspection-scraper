import pymongo
import logging
import sys


class Scoring(object):
    def __init__(self, settings):

        self.score_logger = logging.getLogger('Scoring')
        self.score_logger.setLevel(logging.INFO)

        # Set up database connection (pulled from settings)
        connection = pymongo.MongoClient(
            host=settings['MONGODB_SERVER'],
            port=int(settings['MONGODB_PORT'])
        )

        db = connection[settings['MONGODB_DB']]

        if settings['MONGODB_USER'] and settings['MONGODB_PWD']:
            db.authenticate(settings['MONGODB_USER'], settings['MONGODB_PWD'])

        self.collection = db[settings['MONGODB_COLLECTION']]

        '''
        Weights for calculating the total vendor score.
        The integer indicates how many inspections to use in the score and the
        decimals are the weights for each inspection in descending order by date
        '''
        self.weights = {3: [0.6, 0.3, 0.1],
                        2: [0.7, 0.3],
                        1: [1.0]}
        # The min and max range for the score
        self.score_range = [0, 100]

        # The per inspection scoring. The system is additive.
        self.scoring = {'base': -2.0,
                        'critical': -1.5,
                        'repeat': -1.5,
                        'corrected': 0.5}

    def score_vendors(self):
        vendors = self.collection.find({}, {'inspections': 1, '_id': 1, 'guid': 1})

        for vendor in vendors:
            inspection_scores = []

            if 'inspections' in vendor:
                for inspection in vendor['inspections']:
                    score = self.score_range[1]  # Set score to max

                    # These are the actual calculations for the per inspection score. Modify here to use
                    # different criteria
                    if 'violations' in inspection:
                        for violation in inspection['violations']:
                            score += self.scoring['base']
                            if violation['critical']:
                                score += self.scoring['critical']
                            if violation['repeat']:
                                score += self.scoring['repeat']
                            if violation['corrected']:
                                score += self.scoring['corrected']

                    score = max(score, self.score_range[0])  # Make sure score does not go below min

                    inspection_scores.append([inspection['date'], score])

                    # Update each inspection in DB with score
                    self.collection.update({'_id': vendor['_id'],
                                              'inspections.date': inspection['date']},
                                             {'$set': {'inspections.$.score': score}},
                                             False,
                                             False)
            # Set the correct weight to use based on number of inspections the vendor has
            num_inspections = min(max(self.weights), len(inspection_scores))

            if num_inspections > 0:
                current_weights = self.weights[num_inspections]
                vendor_score = self.score_range[0]

                for i, inspection in enumerate(sorted(inspection_scores, reverse=True)):
                    if i < num_inspections:
                        vendor_score += inspection[1]*current_weights[i]

                self.collection.update({'_id': vendor['_id']},
                                         {'$set': {'score': vendor_score}},
                                         False,
                                         False)

                self.score_logger.info('Record ' + vendor['guid'] + ' scored ' + str(vendor_score))
