"""
K 线数据模型
使用 SQLite 存储币安 K 线数据
"""
import aiosqlite
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# 数据库文件路径
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "kline.db"


class KlineModel:
    """K 线数据模型"""
    
    @staticmethod
    async def init_db():
        """
        初始化数据库表
        创建 klines 表，包含字段：symbol, interval, timestamp (主键), open, high, low, close, volume
        """
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS klines (
                    symbol TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    PRIMARY KEY (symbol, interval, timestamp)
                )
            """)
            
            # 创建索引以提高查询性能
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_interval_timestamp 
                ON klines(symbol, interval, timestamp DESC)
            """)
            
            await db.commit()
            print(f"[OK] K 线数据库初始化成功: {DB_PATH}")
    
    @staticmethod
    async def upsert_klines(klines: List[Dict[str, Any]]):
        """
        批量更新插入 K 线数据（防止重复）
        
        Args:
            klines: K 线数据列表，每个元素包含：
                - symbol: 交易对，如 "BTC/USDT"
                - interval: 时间间隔，如 "1m"
                - timestamp: 时间戳（毫秒）
                - open, high, low, close, volume: OHLCV 数据
        """
        if not klines:
            return
        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.executemany("""
                INSERT OR REPLACE INTO klines 
                (symbol, interval, timestamp, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    kline['symbol'],
                    kline['interval'],
                    kline['timestamp'],
                    kline['open'],
                    kline['high'],
                    kline['low'],
                    kline['close'],
                    kline['volume']
                )
                for kline in klines
            ])
            await db.commit()
    
    @staticmethod
    async def get_klines(
        symbol: str,
        interval: str,
        limit: int = 1000,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        查询 K 线数据
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            interval: 时间间隔，如 "1m"
            limit: 返回数量限制
            start_time: 开始时间戳（毫秒，可选）
            end_time: 结束时间戳（毫秒，可选）
        
        Returns:
            K 线数据列表，按时间戳升序排列
        """
        query = """
            SELECT symbol, interval, timestamp, open, high, low, close, volume
            FROM klines
            WHERE symbol = ? AND interval = ?
        """
        params = [symbol, interval]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp ASC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'symbol': row['symbol'],
                        'interval': row['interval'],
                        'timestamp': row['timestamp'],
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'volume': row['volume']
                    }
                    for row in rows
                ]
    
    @staticmethod
    async def get_latest_timestamp(symbol: str, interval: str) -> Optional[int]:
        """
        获取指定交易对和时间间隔的最新时间戳
        
        Args:
            symbol: 交易对
            interval: 时间间隔
        
        Returns:
            最新时间戳（毫秒），如果没有数据则返回 None
        """
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT MAX(timestamp) as max_ts
                FROM klines
                WHERE symbol = ? AND interval = ?
            """, [symbol, interval]) as cursor:
                row = await cursor.fetchone()
                return row[0] if row and row[0] else None
    
    @staticmethod
    async def count_klines(symbol: str, interval: str) -> int:
        """
        统计指定交易对和时间间隔的 K 线数量
        
        Args:
            symbol: 交易对
            interval: 时间间隔
        
        Returns:
            K 线数量
        """
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT COUNT(*) as cnt
                FROM klines
                WHERE symbol = ? AND interval = ?
            """, [symbol, interval]) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
