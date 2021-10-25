import delimited C:\data\financials\h2_variables.txt, clear
xtset v2 year
gen postxifrs = post*ifrs
xtreg score post ifrs postxifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first, fe robust
xtreg score post ifrs postxifrs adopt droa dcurrent ddebtdue dleverage dfcf merger split big first i.year, fe robust
