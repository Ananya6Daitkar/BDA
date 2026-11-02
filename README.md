## 🌐 FeedOrbit

A **real-time social media feed analytics and recommendation system** that simulates user activities, streams them through Kafka and Spark, stores them in **MongoDB Atlas**, and generates personalized post recommendations using the **ALS (Alternating Least Squares)** algorithm.

---

## 📝 Description / Overview

FeedOrbit is an end-to-end data processing and machine learning pipeline that integrates **Apache Kafka**, **Apache Spark Structured Streaming**, **Scala**, **Python (PySpark)**, and **MongoDB Atlas**.  

It simulates user events such as likes, comments, and shares, ingests them in real time, and then analyzes the data to recommend posts for users.  
The main goal is to demonstrate a **real-time event-driven recommendation engine** using distributed technologies.

---

## 📚 Table of Contents

- [Features](#-features)
- [Installation / Setup](#-installation--setup)
- [Usage / How to Run](#-usage--how-to-run)
- [File Structure](#-file-structure)
- [License](#-license)

---

## ✨ Features

- Simulates random user activities such as **like**, **comment**, **share**, and **view**
- Streams user event data to **Apache Kafka**
- Consumes and processes Kafka streams using **Apache Spark Structured Streaming**
- Stores all processed data in **MongoDB Atlas**
- Trains an **ALS recommendation model** using **PySpark MLlib**
- Generates and stores **user-based post recommendations**
- Demonstrates real-time analytics and batch processing together

---

## ⚙️ Installation and Setup Guide

This section explains how to install and configure all dependencies required to run **FeedOrbit** — including **Python 3.11**, **Apache Spark 3.5.6**, **Scala 2.12.18**, **Java 11**, **Kafka 4.0.0**, and **SBT 1.11.6**.

---

## 🐍 1. Install Python 3.11

**🔗 Download Link:**  
[https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)

### 🧩 Steps
1. Download and install **Python 3.11** for your OS (Windows / Linux / macOS).  
2. During installation, check ✅ **“Add Python to PATH”**.  
3. Verify installation:
   ```bash
   python --version
   ```

**Expected Output:**
```
Python 3.11.x
```

4. Install required Python libraries:

```bash
pip install pyspark pandas pymongo
```

---

## ☕ 2. Install Java 11 (Required for Spark and Kafka)

**🔗 Download Link:**  
[https://adoptium.net/temurin/releases/?version=11](https://adoptium.net/temurin/releases/?version=11)

### 🧩 Steps

1. Download and install the **Temurin JDK 11 (LTS version)**.

2. Set up environment variables:

**Windows:**

* Go to **System Properties → Environment Variables**  
* Add a new variable:

```
JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-11
```

* Add `%JAVA_HOME%\bin` to your **PATH** variable.

**Linux / macOS:**

```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

3. Verify installation:

```bash
java -version
```

**Expected Output:**
```
openjdk version "11.x.x"
```

---

## ⚡ 3. Install Apache Spark 3.5.6

**🔗 Download Link:**  
[https://spark.apache.org/downloads.html](https://spark.apache.org/downloads.html)

### 🧩 Steps

1. Choose:

* Spark version: **3.5.6**  
* Package type: **Pre-built for Apache Hadoop 3**

2. Download and extract it (e.g., `C:\spark-3.5.6-bin-hadoop3`).

3. Add Spark to PATH:

**Windows:**
```
SPARK_HOME=C:\spark-3.5.6-bin-hadoop3
PATH=%SPARK_HOME%\bin;%PATH%
```

**Linux / macOS:**
```bash
export SPARK_HOME=~/spark-3.5.6-bin-hadoop3
export PATH=$SPARK_HOME/bin:$PATH
```

4. Verify Spark installation:

```bash
spark-shell
```

**If the Spark shell opens successfully, installation is complete ✅**

---

## 🧩 4. Install Scala 2.12.18

**🔗 Download Link:**  
[https://www.scala-lang.org/download/2.12.18.html](https://www.scala-lang.org/download/2.12.18.html)

### 🧩 Steps

1. Download and install **Scala 2.12.18**.

2. Add Scala to PATH:

**Windows:**
```
SCALA_HOME=C:\Program Files (x86)\scala
PATH=%SCALA_HOME%\bin;%PATH%
```

**Linux / macOS:**
```bash
export SCALA_HOME=/usr/share/scala
export PATH=$SCALA_HOME/bin:$PATH
```

3. Verify installation:

```bash
scala -version
```

**Expected Output:**
```
Scala code runner version 2.12.18
```

---

## 🧱 5. Install SBT (Scala Build Tool) 1.11.6

**🔗 Download Link:**  
[https://www.scala-sbt.org/download.html](https://www.scala-sbt.org/download.html)

### 🧩 Steps

1. Download and install **SBT 1.11.6**.  
2. Add `sbt\bin` to your system PATH.  
3. Verify installation:

```bash
sbt sbtVersion
```

**Expected Output:**
```
[info] 1.11.6
```

---

## 📡 6. Install Apache Kafka 4.0.0

**🔗 Download Link:**  
[https://kafka.apache.org/downloads](https://kafka.apache.org/downloads)

### 🧩 Steps

1. Download **Kafka 4.0.0** (Scala 2.12 build).  
2. Extract it to your preferred directory (e.g., `C:\kafka` or `/opt/kafka`).  
3. Start **Zookeeper**:

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

4. Start **Kafka Broker**:

```bash
bin/kafka-server-start.sh config/server.properties
```

5. Create a Kafka topic:

```bash
bin/kafka-topics.sh --create --topic test --bootstrap-server localhost:9092
```

6. Verify topic creation:

```bash
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

## ☁️ 7. Setup MongoDB Atlas (Cloud Database)

**🔗 Link:**  
[https://www.mongodb.com/atlas](https://www.mongodb.com/atlas)

### 🧩 Steps

1. Go to the [MongoDB Atlas](https://www.mongodb.com/atlas) website.  
2. Sign up or log in to your account.  
3. Create a **Free Shared Cluster**.  
4. Create a new **database** named `instaFeed`.  
5. Inside the database, create three collections:

* `userEvents`  
* `slidingWindowResults`  
* `recommendations`  

6. Obtain your **connection URI**, e.g.:  
```
mongodb+srv://<username>:<password>@cluster0.mongodb.net/
```

7. Update this URI in your project files:

* `KafkaSparkConsumer.scala`  
* `als_recommendations.py`  

---

## 🖥️ 8. Install Streamlit (for UI Dashboard)



**🔗 Official Site:**  

[https://streamlit.io](https://streamlit.io)



Streamlit is used in **FeedOrbit** to build a simple, interactive **web UI** for visualizing analytics and personalized post recommendations fetched from MongoDB Atlas.



### 🧩 Steps



1. Install Streamlit via pip:

   ```bash

   pip install streamlit pymongo pandas

   ```



2. Verify installation:

   ```bash

   streamlit --version

   ```



   **Expected Output:**

   ```

   streamlit, version X.X.X

   ```



3. Create a UI file (for example, `app.py`) in your project directory:

   ```python

   import streamlit as st

   import pandas as pd

   from pymongo import MongoClient



   # MongoDB connection

   client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/")

   db = client["instaFeed"]



   st.title("📊 FeedOrbit - Real-Time Recommendations Dashboard")



   # Show latest user events

   st.subheader("🧩 Recent User Events")

   events = list(db.userEvents.find().sort("_id", -1).limit(20))

   st.dataframe(pd.DataFrame(events))



   # Show latest recommendations

   st.subheader("⭐ Latest Recommendations")

   recs = list(db.recommendations.find().sort("_id", -1).limit(10))

   st.dataframe(pd.DataFrame(recs))

   ```



4. Run the Streamlit app:

   ```bash

   streamlit run app.py

   ```



5. The dashboard will open automatically in your browser (default: `http://localhost:8501`).



---

## ✅ Verification Summary

| Component         | Command                                                        | Expected Output         |
| ----------------- | -------------------------------------------------------------- | ----------------------- |
| **Python**        | `python --version`                                             | 3.11.x                  |
| **Java**          | `java -version`                                                | 11.x                    |
| **Scala**         | `scala -version`                                               | 2.12.18                 |
| **Spark**         | `spark-shell`                                                  | Spark 3.5.6 shell opens |
| **Kafka**         | `bin/kafka-topics.sh --list --bootstrap-server localhost:9092` | Lists topics            |
| **SBT**           | `sbt sbtVersion`                                               | 1.11.6                  |
| **MongoDB Atlas** | Connect using URI                   
| **Streamlit**     | `streamlit --version`                                          | Displays version number |
    
 ## 🚀 Usage / How to Run



Once all dependencies are installed and configured, you can run **FeedOrbit** in the following steps:



### 1️⃣ Start Kafka Broker

```bash

cd kafka

sbt run

```



### 2️⃣ Create Kafka Topics

```bash

bin/kafka-topics.sh --create --topic userEvents --bootstrap-server localhost:9092

bin/kafka-topics.sh --create --topic recommendations --bootstrap-server localhost:9092

```



### 3️⃣ Run Spark Consumer

```bash

spark-submit --class KafkaSparkConsumer target/scala-2.12/kafka-spark-consumer_2.12-0.1.jar

```



### 4️⃣ Run ALS Recommendation SRecommendation_FeedOrbithon als_recommendations.py

```



### 5️⃣ Launch Streamlitui

```bash

streamlit run app.py

```



Open your browser at [http://localhost:8501](http://localhost:8501) to view the live FeedOrbit dashboard showing:

- Real-time user activity streams  

- Generated ALS recommendations  



### 6️⃣ Verify MongoDB Collections

Check `userEvents`, `slidingWindowResults`, and `recommendations` in your **MongoDB Atlas** cluster.



---nd recommendations in your MongoDB Atlas cluster.

---

## 📁 File Structure

```
FeedOrbit/
├─ 📄 README.md                    # Project documentation and instructions
├─ ⚡ KafkaProducer.scala           # Simulates user events and sends to Kafka
├─ ⚡ KafkaSparkConsumer.scala      # Consumes Kafka events and p
├─ 🖥️ app.py                         # Streamlit dashboard for visualizing events & recommendationsrocesses with Spark
├─ 🐍 als_recommendations.py        # Generates ALS-based recommendations
├─ 📦 requirements.txt              # Python dependencies
├─ ⚙️ build.sbt                     # Scala / SBT build configuration
├─ 🗂️ data/                         # Sample input data files (optional)
├─ 🗂️ output/                       # Generated recommendation results
└─ 📓 notebooks/                    # Jupyter notebooks for testing & analysis
```

---



# 📄 License

© 2025. All rights reserved.

This is a personal project created from scratch with original code, design, and implementation.
Not open for external contributions.
