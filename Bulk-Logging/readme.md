# 📂 Bulk Logging & File Operations – FAANG LLD Question Bank

This document lists **Low-Level Design (LLD)** style questions that FAANG and other top product companies often ask around **logging, file operations, caching, concurrency, and scalability**.

---

## **1. Core Logging System**
- Design a **logging framework** that supports multiple log levels (INFO, DEBUG, ERROR, WARN).
- How would you store logs in memory before writing to disk?
- How would you make the logger **thread-safe**?

---

## **2. Bulk / Batch Logging**
- Design a **bulk logging system** that collects logs in memory and flushes them in batches.
  - Flush when buffer size reaches X MB OR after Y seconds.
  - How do you handle **buffer overflow** when logs arrive faster than they can be flushed?
  - How do you minimize **latency vs throughput** tradeoff?

---

## **3. File Storage & Operations**
- Logs must be stored in **files**. Design the file storage module:
  - Support **rotation** (time-based or size-based).
  - Support **archival** (move older logs to compressed files / cloud).
  - Allow **parallel writes** without corruption.
  - How would you support **read while write**?

---

## **4. Searching & Querying Logs**
- Design a feature to **search logs** efficiently.
  - Query by timestamp range.
  - Query by log level (only ERROR).
  - Query by text substring.
- Would you build **indexes** on logs? Where would you store them?
- How would you support **real-time queries** while logs are still being written?

---

## **5. Concurrency & Threading**
- Multiple threads generate logs. Design the concurrency mechanism.
  - How do you ensure logs from different threads don’t interleave/corrupt?
  - How do you support **async logging** so the application isn’t blocked?
  - Would you use **locks or lock-free queues**? Why?
  - How do you handle **concurrent log rotation + writes**?

---

## **6. Message Queue Integration**
- Extend your logging framework to use a **message queue** (Kafka/RabbitMQ).
  - Logs are pushed into the queue, and a consumer writes them in batches to disk.
  - How would you guarantee **ordering** of logs?
  - How do you handle **backpressure** if producers are faster than consumers?
  - How would you ensure **at-least-once delivery**?

---

## **7. Caching Layer**
- Design a **log cache** for faster reads.
  - Which logs would you keep in cache? (recent ones? ERROR logs?)
  - What eviction policy would you use (**LRU, LFU, TTL**)?
  - How do you keep **cache and file storage consistent**?

---

## **8. Fault Tolerance & Recovery**
- The logging process crashes — how do you ensure no logs are lost?
  - Would you use a **Write-Ahead Log (WAL)**?
  - How do you recover unflushed logs on restart?
  - Disk is full — what should happen? Drop logs, block writers, or purge old logs?
  - What’s your retry mechanism for failed flushes?

---

## **9. Distributed Logging**
- Extend your design to support **multiple servers** generating logs.
  - How do you aggregate logs centrally?
  - How would you partition logs (by time, service, or level)?
  - How would you ensure **ordering** across distributed sources?
  - How would you make the system **highly available** (HA)?

---

## **10. Extensibility**
- Logs should not only go to files — but also to:
  - Database (Postgres, Cassandra, ElasticSearch)
  - External systems (Kafka, S3, BigQuery)
  - Real-time monitoring dashboards
- Design your logging system so that it is **pluggable** with multiple “sinks.”

---

## **11. Advanced Features**
- Add support for **structured logs** (JSON with metadata).
- Add support for **log sampling** (skip some INFO logs under heavy load).
- Add support for **dynamic log filtering** at runtime (only capture ERROR logs).
- Add support for **log replay** (feed past logs back into the system).
- Add support for **multi-tenancy** (different apps using same logger).

---

## **12. Scalability Questions**
- How do you design the system to handle **1M logs/sec**?
- How do you shard logs across multiple files/machines?
- How would you compress logs without impacting write performance?
- How do you design for **real-time ingestion + querying** like ELK / Splunk?

---

## **13. Tradeoff Discussion**
- Tradeoff between **sync vs async logging**.
- Tradeoff between **batch size vs latency**.
- Tradeoff between **file storage vs DB storage**.
- Tradeoff between **queue-based vs direct file writes**.
- Tradeoff between **compressed logs vs searchable logs**.

---

✅ With these 13 sections of questions, you’ll cover:
- **Storage (files, DB, cloud)**
- **Search (query, index, filtering)**
- **Concurrency (thread-safe, batching)**
- **Performance (buffering, caching)**
- **Reliability (crash recovery, WAL)**
- **Scalability (distributed logging, MQ)**
- **Extensibility (multi sinks, filters, structured logs)**
