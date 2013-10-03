library(stringr)
library(lubridate)
library(ggplot2)

r <- read.csv("testrun.csv", sep="\t", header=FALSE)
C <- as.numeric(str_sub(r$V1, -4, -1))
T <- ymd_hms(str_sub(r$V1, 1, -7))

d <- data.frame(time = T, temp = C)

ggplot(d, aes(T, C)) + geom_line()
