"""Card approval thresholds matching frontend"""

CARD_THRESHOLDS = {
    "legionnaire": {
        "highlyQualified": {
            "minSalary": 75000,
            "minNetWorth": 0,
            "minAge": 25,
            "minFico": 720
        },
        "likely": {
            "minSalary": 50000,
            "minNetWorth": 0,
            "minAge": 21,
            "minFico": 700
        }
    },
    "tribune": {
        "highlyQualified": {
            "minSalary": 200000,
            "minNetWorth": 1000000,
            "minAge": 30,
            "minFico": 800
        },
        "likely": {
            "minSalary": 150000,
            "minNetWorth": 800000,
            "minAge": 25,
            "minFico": 750
        }
    }
}
