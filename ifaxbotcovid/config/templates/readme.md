# How to use

Put name of variable in curly brackets {}.

Example:

*Today we've got {russia_new_cases} new COVID-19 cases in Russia and {russia_new_deaths} deaths.*

flashtemplate.txt - for flash
rpntemplate.txt - for rpn
texttemplate.txt - for main text

# List of avaliable variables for templates

### FOR COVID-19 DAILY RELEASE:

russia_new_cases        # new COVID-19 cases in Russia for the last 24h 
russia_current_pace     # difference of total COVID-19 cases in % between today and yesterday
russia_new_deaths       # COVID-related deaths in Russia for the last 24h
russia_new_recovered    # patients recovered after COVID for the last 24h
russia_total_cases      # total COVID-19 cases in Russia for present
russia_total_deaths     # total COVID-related deaths in Russia for present
russia_total_recovered  # total number of patients recovered after COVID-19 in Russia
russia_active           # active COVID cases: <total cases> - (<total recoverd> + <total dead>)
moscow_new_cases        # Moscow COVID-19 cases for 24h
moscow_new_deaths       # Moscow COVID-related deaths for 24h
moscow_new_recovered    # Moscow recovered COVID-patients for 24h 

date_dateline           # formatted date and month for dateline string in Russian ("12 января") 
date_day                # day of the week in Russian put in right grammatical form
golden_cite             # a piece of original raw text for the second paragraph

### FOR RPN COVID-TESTING DAILY MESSAGE:

'total_tests'           # total number of COVID-19 tests performed in Russia
'recent_tests'          # number of COVID tests for the last 24h
'people_monitored'      # number of patients under medical control after COVID contact