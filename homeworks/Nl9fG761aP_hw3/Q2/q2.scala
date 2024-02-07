// Databricks notebook source
// STARTER CODE - DO NOT EDIT THIS CELL
import org.apache.spark.sql.functions.desc
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import spark.implicits._
import org.apache.spark.sql.expressions.Window

// COMMAND ----------

// STARTER CODE - DO NOT EDIT THIS CELL
spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")

// COMMAND ----------

// STARTER CODE - DO NOT EDIT THIS CELL
val customSchema = StructType(Array(StructField("lpep_pickup_datetime", StringType, true), StructField("lpep_dropoff_datetime", StringType, true), StructField("PULocationID", IntegerType, true), StructField("DOLocationID", IntegerType, true), StructField("passenger_count", IntegerType, true), StructField("trip_distance", FloatType, true), StructField("fare_amount", FloatType, true), StructField("payment_type", IntegerType, true)))

// COMMAND ----------

// STARTER CODE - YOU CAN LOAD ANY FILE WITH A SIMILAR SYNTAX.
val df = spark.read
   .format("com.databricks.spark.csv")
   .option("header", "true") // Use first line of all files as header
   .option("nullValue", "null")
   .schema(customSchema)
   .load("/FileStore/tables/nyc_tripdata.csv") // the csv file which you want to work with
   .withColumn("pickup_datetime", from_unixtime(unix_timestamp(col("lpep_pickup_datetime"), "MM/dd/yyyy HH:mm")))
   .withColumn("dropoff_datetime", from_unixtime(unix_timestamp(col("lpep_dropoff_datetime"), "MM/dd/yyyy HH:mm")))
   .drop($"lpep_pickup_datetime")
   .drop($"lpep_dropoff_datetime")

// COMMAND ----------

// LOAD THE "taxi_zone_lookup.csv" FILE SIMILARLY AS ABOVE. CAST ANY COLUMN TO APPROPRIATE DATA TYPE IF NECESSARY.
// ENTER THE CODE BELOW
val df_lookup = spark.read
   .format("com.databricks.spark.csv")
   .option("header", "true") // Use first line of all files as header
   .option("nullValue", "null")
   // .schema(customSchema)
   .load("/FileStore/tables/taxi_zone_lookup.csv") // the csv file which you want to work with

df_lookup.show(5)

// COMMAND ----------

// STARTER CODE - DO NOT EDIT THIS CELL
// Some commands that you can use to see your dataframes and results of the operations. You can comment the df.show(5) and uncomment display(df) to see the data differently. You will find these two functions useful in reporting your results.
// display(df)
df.show(5) // view the first 5 rows of the dataframe

// COMMAND ----------

// STARTER CODE - DO NOT EDIT THIS CELL
// Filter the data to only keep the rows where "PULocationID" and the "DOLocationID" are different and the "trip_distance" is strictly greater than 2.0 (>2.0).

// VERY VERY IMPORTANT: ALL THE SUBSEQUENT OPERATIONS MUST BE PERFORMED ON THIS FILTERED DATA

val df_filter = df.filter($"PULocationID" =!= $"DOLocationID" && $"trip_distance" > 2.0)
df_filter.show(5)

// COMMAND ----------

// PART 1a: List the top-5 most popular locations for dropoff based on "DOLocationID", sorted in descending order by popularity. If there is a tie, then the one with the lower "DOLocationID" gets listed first

// Output Schema: DOLocationID int, number_of_dropoffs int 

// Hint: Checkout the groupBy(), orderBy() and count() functions.

// ENTER THE CODE BELOW
val popularDO = df_filter.groupBy("DOLocationID")
  .agg(count("*").alias("number_of_dropoffs"))
  .orderBy(desc("number_of_dropoffs"), asc("DOLocationID"))
popularDO.show(5)

// COMMAND ----------

// PART 1b: List the top-5 most popular locations for pickup based on "PULocationID", sorted in descending order by popularity. If there is a tie, then the one with the lower "PULocationID" gets listed first.
 
// Output Schema: PULocationID int, number_of_pickups int

// Hint: Code is very similar to part 1a above.

// ENTER THE CODE BELOW
val popularPU = df_filter.groupBy("PULocationID")
  .agg(count("*").alias("number_of_pickups"))
  .orderBy(desc("number_of_pickups"), asc("PULocationID"))
popularPU.show(5)

// COMMAND ----------

// PART 2: List the top-3 locationID’s with the maximum overall activity. Here, overall activity at a LocationID is simply the sum of all pickups and all dropoffs at that LocationID. In case of a tie, the lower LocationID gets listed first.

//Note: If a taxi picked up 3 passengers at once, we count it as 1 pickup and not 3 pickups.

// Output Schema: LocationID int, number_activities int

// Hint: In order to get the result, you may need to perform a join operation between the two dataframes that you created in earlier parts (to come up with the sum of the number of pickups and dropoffs on each location). 

// ENTER THE CODE BELOW
val pickupAlias = popularPU
  .withColumnRenamed("PULocationID", "LocationID")
  .withColumnRenamed("number_of_pickups", "number_activities")

val dropoffAlias = popularDO
  .withColumnRenamed("DOLocationID", "LocationID")
  .withColumnRenamed("number_of_dropoffs", "number_activities")

val overallActivity = pickupAlias.union(dropoffAlias)

val groupedData = overallActivity
  .groupBy("LocationID")
  .agg(sum("number_activities").as("number_activities"))

val topLocations = groupedData
  .orderBy(desc("number_activities"), asc("LocationID"))
  .limit(3)

// Show the result
topLocations.show()

// COMMAND ----------

// PART 3: List all the boroughs (of NYC: Manhattan, Brooklyn, Queens, Staten Island, Bronx along with "Unknown" and "EWR") and their total number of activities, in descending order of total number of activities. Here, the total number of activities for a borough (e.g., Queens) is the sum of the overall activities (as defined in part 2) of all the LocationIDs that fall in that borough (Queens). 

// Output Schema: Borough string, total_number_activities int

// Hint: You can use the dataframe obtained from the previous part, and will need to do the join with the 'taxi_zone_lookup' dataframe. Also, checkout the "agg" function applied to a grouped dataframe.

// ENTER THE CODE BELOW
// overallActivity.show(10)

val locationWithBorough = overallActivity
  .join(df_lookup, Seq("LocationID"), "left")

// locationWithBorough.show(10)

val boroughs = locationWithBorough
  .groupBy("Borough")
  .agg(sum("number_activities").cast("int").as("total_number_activities"))

val sortedBoroughs = boroughs
  .orderBy(desc("total_number_activities"))

sortedBoroughs.show()

// COMMAND ----------

// PART 4: List the top 2 days of week with the largest number of daily average pickups, along with the average number of pickups on each of the 2 days in descending order (no rounding off required). Here, the average pickup is calculated by taking an average of the number of pick-ups on different dates falling on the same day of the week. For example, 02/01/2021, 02/08/2021 and 02/15/2021 are all Mondays, so the average pick-ups for these is the sum of the pickups on each date divided by 3.

//Note: The day of week is a string of the day’s full spelling, e.g., "Monday" instead of the		number 1 or "Mon". Also, the pickup_datetime is in the format: yyyy-mm-dd.

// Output Schema: day_of_week string, avg_count float

// Hint: You may need to group by the "date" (without time stamp - time in the day) first. Checkout "to_date" function.

// ENTER THE CODE BELOW
val dayOfWeek = df_filter
  .withColumn("day_of_week", date_format($"pickup_datetime", "EEEE"))

val dataWithDate = dayOfWeek
  .withColumn("date", to_date($"pickup_datetime"))

val dataByDay = dataWithDate
  .groupBy("day_of_week", "date")
  .agg(sum("passenger_count").alias("daily_pickups"))

val averageDaily = dataByDay
  .groupBy("day_of_week")
  .agg(avg("daily_pickups").cast("float").as("avg_count"))

val sortedAveragePickups = averageDaily
  .orderBy(desc("avg_count"))

val top2Days = sortedAveragePickups.limit(2)

top2Days.show()

// COMMAND ----------

// PART 5: For each hour of a day (0 to 23, 0 being midnight) - in the order from 0 to 23(inclusively), find the zone in the Brooklyn borough with the LARGEST number of total pickups. 

//Note: All dates for each hour should be included.

// Output Schema: hour_of_day int, zone string, max_count int

// Hint: You may need to use "Window" over hour of day, along with "group by" to find the MAXIMUM count of pickups

// ENTER THE CODE BELOW
val dfWithBorough = df_filter
  .join(df_lookup, df_filter("PULocationID") === df_lookup("LocationID"), "left")

// dfWithBorough.show()

val dataWithHourOfDay = dfWithBorough
  .withColumn("hour_of_day", hour($"pickup_datetime"))

val brooklynPickups = dataWithHourOfDay
  .filter($"Borough" === "Brooklyn")

val hourlyZonePickups = brooklynPickups
  .groupBy("hour_of_day", "Zone")
  .agg(count("*").alias("pickup_count"))

val windowSpec = Window.partitionBy("hour_of_day").orderBy(desc("pickup_count"))

val rankedBrooklynPickups = hourlyZonePickups
  .withColumn("rank", dense_rank().over(windowSpec))
  .filter($"rank" === 1)

val output = rankedBrooklynPickups.select("hour_of_day", "Zone", "pickup_count")

output.show(24)

// COMMAND ----------

// PART 6 - Find which 3 different days in the month of January, in Manhattan, saw the largest positive percentage increase in pick-ups compared to the previous day, in the order from largest percentage increase to smallest percentage increase 

// Note: All years need to be aggregated to calculate the pickups for a specific day of January. The change from Dec 31 to Jan 1 can be excluded.

// Output Schema: day int, percent_change float


// Hint: You might need to use lag function, over a window ordered by day of month.

// ENTER THE CODE BELOW

// dfWithBorough.show()

val januaryManhattanPickups = dfWithBorough
  .filter($"Borough" === "Manhattan" && month($"pickup_datetime") === 1)

// januaryManhattanPickups.show()
// val windowSpec = Window.orderBy(dayofmonth($"pickup_datetime"))

val dailyPickups = januaryManhattanPickups
  .groupBy(dayofmonth($"pickup_datetime").alias("day"))
  .agg(count("*").alias("pickups"))

// dailyPickups.show()

val lagPickups = dailyPickups
  .withColumn("lag_pickups", lag("pickups", 1).over(Window.orderBy("day")))

val percentChange = lagPickups
  .withColumn("percent_change", (col("pickups") - col("lag_pickups")) / col("lag_pickups") * 100)

val filteredResults = percentChange.filter(col("day") > 1)

val sortedResults = filteredResults
  .orderBy(desc("percent_change"))

val top3Days = sortedResults
  .select("day", "percent_change")
  .limit(3)

top3Days.show()

// COMMAND ----------


