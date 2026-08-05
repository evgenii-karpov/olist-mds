package com.olist.mds.spark.silver

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.locks.ReentrantLock

object IcebergCommitCoordinator {
  private val locks = new ConcurrentHashMap[String, ReentrantLock]()

  def lockForTable(tableName: String): ReentrantLock = {
    locks.computeIfAbsent(tableName, _ => new ReentrantLock(true))
  }

  def withLock[T](tableName: String)(block: => T): T = {
    val lock = lockForTable(tableName)
    lock.lock()
    try {
      block
    } finally {
      lock.unlock()
    }
  }
}
