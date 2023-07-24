# FF-VARIANCE-FACTOR

This repository is dedicated to the construction and analysis of a unique daily 'variance factor'. This factor represents the daily performance differential between high-variance stocks and low-variance stocks.

Here's a snapshot of our work:

Replication of Fama French's Monthly Variance Portfolios: Our first step is to replicate the decile variance portfolios initially proposed by Fama French. Using Real-Time Price Data and Zacks Fundamentals Data, we successfully mirror these 10 decile variance portfolios with a 99% correlation (Note: Fama French's portfolios are constructed using CRSP Data).

Construction of Daily Variance Factor: Building on the previous step, we devise a unique variance factor based on daily data. This factor is calculated as the return on the high-variance value-weighted portfolio minus the return on the low-variance value-weighted portfolio. This methodology follows a similar approach to that of Fama French but adapts it to a daily timeframe.

Through these efforts, we aim to offer valuable insights into the dynamic behavior of high and low-variance stocks and to provide an innovative tool for performance comparison on a daily basis.
