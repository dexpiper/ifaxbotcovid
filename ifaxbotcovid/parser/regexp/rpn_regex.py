'''
Regular expressions for short COVID-19 testing report
by Russian watchdog Rospotrebnadzor (aka RPN)
'''

rpn_regex = {
    'total_tests': r'РФ проведен\w? более (\d+,?\d?) млн\.? тест\w+ на корона',
    'recent_tests': r'за сутки проведено (\d+) тыс. тестов на коронав',
    'people_monitored': (
        r'под меднаблюдением оста\wтся (\d{0,3}\s?\d+\s\d+)\s{1,3}чел'
    )
}
