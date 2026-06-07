---
title: "HPE Sustainability Insight Center glossary"
source_url: "https://developer.greenlake.hpe.com/docs/greenlake/services/sustainability/public/glossary.md"
scraped_at: "2026-06-07T05:46:14.668332+00:00Z"
---

# HPE Sustainability Insight Center glossary

## Acronyms

### CO2e

Carbon dioxide equivalent emissions. For greenhouse gases other than CO2, this is the amount of CO2 that has an equivalent environmental impact to the measured amount of that greenhouse gas.

### kWh

A kilowatt-hour (kWh) is a unit for measuring electricity defined as 1 kilowatt of power sustained for 1 hour.

## Terms

### Entity

An entity in this API could be anything with reportable power usage measurements. This includes HPE products or energy-consuming products not sold by HPE but reported to the HPE Sustainability Insight Center.

### Greenhouse gas

Greenhouse gas (GHG) emissions are sometimes referred to as simply “carbon emissions” because carbon-based compounds, such as carbon dioxide and carbon monoxide, tend to be the most detrimental emissions produced by many industries and enterprises. Furthermore, to simplify reporting on GHG emissions, all GHGs other than carbon dioxide (CO2) are converted into their equivalent CO2 emissions (CO2e). We use the term “carbon emissions” for its simplicity and colloquial popularity, but the emissions reported are in fact GHG emissions in units of CO2e.

### Time series

A time series is a dataset in an ordered sequence of values at equally spaced intervals (time buckets). For example, the HPE Sustainability Insight Center can provide measures of daily energy consumption for HPE entities. The energy consumption is the value, and the time bucket is daily.

Time series data facilitates statistical time series analysis and forecasting. For example, using the daily energy consumption data:

- You could analyze historical trends for spikes or dips in energy consumption.
- You could make predictive inferences about future energy use.


The **Get energy usage series** API returns data suitable for time series analysis.