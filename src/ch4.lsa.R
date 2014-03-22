x <- c(0, 1, 2, 3)
y <- c(-1, 0.2, 0.9, 2.1)
df <- data.frame(x, y)

m <- lm(df$y ~ df$x)

plot(df)
abline(m, col="red")