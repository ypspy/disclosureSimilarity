library(plm)
options(scipen=999)

Panel <- read.csv("C:/data/car/h2_variables.txt")

fixed <- plm(car_val ~ score + filelate + car_e_val + lnAsset
             + modified + gc + factor(year)
             , data=Panel, index=c("X10", "year")
             , effect = "twoway" 
             , model="within")

summary(fixed)
