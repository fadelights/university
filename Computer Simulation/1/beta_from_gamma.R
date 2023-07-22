# Generating Beta random variates from Gamma distribution using transformations
# If U ~ Gamma(a, lambda) and
#    V ~ Gamma(b, lambda)
# then U/(U+V) ~ Beta(a, b)

n <- 1000  # number of required samples
a <- 3
b <- 2

u <- rgamma(n, shape = a, rate = 1)
v <- rgamma(n, shape = b, rate = 1)

x <- u / (u + v)

# comparing actual beta dist with generated rvs
# points <- seq(0, 1, length.out=n)
points <- ppoints(n)
beta_rvs <- qbeta(points, a, b)

qqplot(beta_rvs, x,
       pch = 16, cex = .5, col = gray(0, .1),
       xlab = "Beta Random Variates", ylab = "Generated Samples")
abline(0, 1)
