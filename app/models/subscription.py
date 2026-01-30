"""
认购/Launchpad 数据模型
使用 SQLite 存储认购项目数据和用户认购记录
支持高精度加密货币金额（使用 TEXT 存储 Decimal 字符串，避免浮点数误差）
"""
import aiosqlite
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal, ROUND_DOWN, InvalidOperation


# 数据库文件路径（与 kline.db 在同一目录）
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "subscription.db"


class SubscriptionModel:
    """认购数据模型"""
    
    @staticmethod
    async def init_db():
        """
        初始化数据库表
        创建 subscription_projects 和 subscription_orders 两个表
        """
        async with aiosqlite.connect(DB_PATH) as db:
            # 创建认购项目表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscription_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    currency TEXT NOT NULL,
                    token_name TEXT NOT NULL,
                    price TEXT NOT NULL,
                    total_cap TEXT NOT NULL,
                    current_raised TEXT NOT NULL DEFAULT '0',
                    min_buy_amount TEXT NOT NULL,
                    max_buy_user TEXT NOT NULL,
                    start_time INTEGER NOT NULL,
                    end_time INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    lock_period INTEGER,
                    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # 创建用户认购记录表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS subscription_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    project_id INTEGER NOT NULL,
                    amount TEXT NOT NULL,
                    token_amount TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
                    FOREIGN KEY (project_id) REFERENCES subscription_projects(id)
                )
            """)
            
            # 创建索引以提高查询性能
            # 项目表索引：按状态和时间查询
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_status 
                ON subscription_projects(status)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_time 
                ON subscription_projects(start_time, end_time)
            """)
            
            # 订单表索引：按用户、项目、状态查询
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_user_id 
                ON subscription_orders(user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_project_id 
                ON subscription_orders(project_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_status 
                ON subscription_orders(status)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_user_project 
                ON subscription_orders(user_id, project_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_created_at 
                ON subscription_orders(created_at DESC)
            """)
            
            await db.commit()
            print(f"[OK] 认购数据库初始化成功: {DB_PATH}")
    
    @staticmethod
    def _decimal_to_str(value: Any) -> str:
        """
        将 Decimal 或数值转换为字符串（用于存储到数据库）
        
        Args:
            value: Decimal、float、int 或字符串
            
        Returns:
            str: 十进制字符串表示
        """
        if value is None:
            return "0"
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, (int, float)):
            return str(Decimal(str(value)))
        if isinstance(value, str):
            # 验证字符串是否为有效数字
            try:
                Decimal(value)
                return value
            except InvalidOperation:
                raise ValueError(f"无效的数值字符串: {value}")
        raise TypeError(f"不支持的类型: {type(value)}")
    
    @staticmethod
    def _str_to_decimal(value: str) -> Decimal:
        """
        将字符串转换为 Decimal（从数据库读取时使用）
        
        Args:
            value: 十进制字符串
            
        Returns:
            Decimal: Decimal 对象
        """
        if value is None:
            return Decimal("0")
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return Decimal("0")
    
    # ========== 项目相关方法 ==========
    
    @staticmethod
    async def create_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建认购项目
        
        Args:
            project_data: 项目数据字典，包含：
                - currency: 认购币种（如 "USDT"）
                - token_name: 发行代币名称（如 "NEWCOIN"）
                - price: 兑换价格（1 Token = ? Currency）
                - total_cap: 项目总募资硬顶
                - min_buy_amount: 单笔最小认购额
                - max_buy_user: 单个用户累计最大认购额
                - start_time: 认购开始时间（Unix 时间戳，秒）
                - end_time: 认购结束时间（Unix 时间戳，秒）
                - status: 状态（可选，默认 "Pending"）
                - lock_period: 锁仓周期（天，可选）
        
        Returns:
            dict: 创建的项目信息（包含 id）
        """
        # 转换金额字段为字符串
        project_data = project_data.copy()
        project_data["price"] = SubscriptionModel._decimal_to_str(project_data.get("price", "0"))
        project_data["total_cap"] = SubscriptionModel._decimal_to_str(project_data.get("total_cap", "0"))
        project_data["current_raised"] = SubscriptionModel._decimal_to_str(project_data.get("current_raised", "0"))
        project_data["min_buy_amount"] = SubscriptionModel._decimal_to_str(project_data.get("min_buy_amount", "0"))
        project_data["max_buy_user"] = SubscriptionModel._decimal_to_str(project_data.get("max_buy_user", "0"))
        
        # 设置默认值
        project_data.setdefault("status", "Pending")
        project_data.setdefault("current_raised", "0")
        
        # 时间戳处理（如果传入的是 datetime，转换为时间戳）
        if isinstance(project_data.get("start_time"), datetime):
            project_data["start_time"] = int(project_data["start_time"].timestamp())
        if isinstance(project_data.get("end_time"), datetime):
            project_data["end_time"] = int(project_data["end_time"].timestamp())
        
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO subscription_projects 
                (currency, token_name, price, total_cap, current_raised, min_buy_amount, 
                 max_buy_user, start_time, end_time, status, lock_period, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%s', 'now'), strftime('%s', 'now'))
            """, (
                project_data["currency"],
                project_data["token_name"],
                project_data["price"],
                project_data["total_cap"],
                project_data["current_raised"],
                project_data["min_buy_amount"],
                project_data["max_buy_user"],
                project_data["start_time"],
                project_data["end_time"],
                project_data["status"],
                project_data.get("lock_period"),
            ))
            await db.commit()
            project_id = cursor.lastrowid
            
            # 返回创建的项目
            return await SubscriptionModel.get_project(project_id)
    
    @staticmethod
    async def get_project(project_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个项目信息
        
        Args:
            project_id: 项目 ID
            
        Returns:
            dict: 项目信息，如果不存在则返回 None
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT id, currency, token_name, price, total_cap, current_raised,
                       min_buy_amount, max_buy_user, start_time, end_time, status,
                       lock_period, created_at, updated_at
                FROM subscription_projects
                WHERE id = ?
            """, [project_id]) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
                return {
                    "id": row["id"],
                    "currency": row["currency"],
                    "token_name": row["token_name"],
                    "price": row["price"],  # 保持字符串格式，前端可转换为 Decimal
                    "total_cap": row["total_cap"],
                    "current_raised": row["current_raised"],
                    "min_buy_amount": row["min_buy_amount"],
                    "max_buy_user": row["max_buy_user"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                    "status": row["status"],
                    "lock_period": row["lock_period"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
    
    @staticmethod
    async def list_projects(
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取项目列表
        
        Args:
            status: 可选，筛选特定状态的项目
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            list: 项目列表
        """
        query = """
            SELECT id, currency, token_name, price, total_cap, current_raised,
                   min_buy_amount, max_buy_user, start_time, end_time, status,
                   lock_period, created_at, updated_at
            FROM subscription_projects
        """
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "currency": row["currency"],
                        "token_name": row["token_name"],
                        "price": row["price"],
                        "total_cap": row["total_cap"],
                        "current_raised": row["current_raised"],
                        "min_buy_amount": row["min_buy_amount"],
                        "max_buy_user": row["max_buy_user"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "status": row["status"],
                        "lock_period": row["lock_period"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    }
                    for row in rows
                ]
    
    @staticmethod
    async def update_project(project_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新项目信息
        
        Args:
            project_id: 项目 ID
            updates: 要更新的字段字典
            
        Returns:
            dict: 更新后的项目信息，如果项目不存在则返回 None
        """
        # 转换金额字段
        updates = updates.copy()
        for key in ["price", "total_cap", "current_raised", "min_buy_amount", "max_buy_user"]:
            if key in updates:
                updates[key] = SubscriptionModel._decimal_to_str(updates[key])
        
        # 构建更新 SQL
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ["price", "total_cap", "current_raised", "min_buy_amount", "max_buy_user",
                      "currency", "token_name", "start_time", "end_time", "status", "lock_period"]:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return await SubscriptionModel.get_project(project_id)
        
        set_clauses.append("updated_at = strftime('%s', 'now')")
        params.append(project_id)
        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f"""
                UPDATE subscription_projects
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, params)
            await db.commit()
            
            return await SubscriptionModel.get_project(project_id)
    
    @staticmethod
    async def update_project_raised(project_id: int, additional_amount: Any) -> Optional[Dict[str, Any]]:
        """
        更新项目的已募资金额（原子操作）
        
        Args:
            project_id: 项目 ID
            additional_amount: 增加的金额（Decimal、float、int 或字符串）
            
        Returns:
            dict: 更新后的项目信息
        """
        additional_amount_str = SubscriptionModel._decimal_to_str(additional_amount)
        
        async with aiosqlite.connect(DB_PATH) as db:
            # 使用 SQL 原子更新
            await db.execute("""
                UPDATE subscription_projects
                SET current_raised = CAST(current_raised AS REAL) + CAST(? AS REAL),
                    updated_at = strftime('%s', 'now')
                WHERE id = ?
            """, [additional_amount_str, project_id])
            await db.commit()
            
            return await SubscriptionModel.get_project(project_id)
    
    # ========== 订单相关方法 ==========
    
    @staticmethod
    async def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建用户认购订单
        
        Args:
            order_data: 订单数据字典，包含：
                - user_id: 用户钱包地址（小写）
                - project_id: 项目 ID
                - amount: 支付金额
                - token_amount: 获得代币数量
                - status: 订单状态（可选，默认 "Pending"）
        
        Returns:
            dict: 创建的订单信息（包含 id）
        """
        order_data = order_data.copy()
        
        # 转换金额字段
        order_data["amount"] = SubscriptionModel._decimal_to_str(order_data.get("amount", "0"))
        order_data["token_amount"] = SubscriptionModel._decimal_to_str(order_data.get("token_amount", "0"))
        
        # 确保 user_id 是小写
        order_data["user_id"] = str(order_data.get("user_id", "")).lower()
        
        # 设置默认状态
        order_data.setdefault("status", "Pending")
        
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("""
                INSERT INTO subscription_orders
                (user_id, project_id, amount, token_amount, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, strftime('%s', 'now'), strftime('%s', 'now'))
            """, (
                order_data["user_id"],
                order_data["project_id"],
                order_data["amount"],
                order_data["token_amount"],
                order_data["status"],
            ))
            await db.commit()
            order_id = cursor.lastrowid
            
            # 返回创建的订单
            return await SubscriptionModel.get_order(order_id)
    
    @staticmethod
    async def get_order(order_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个订单信息
        
        Args:
            order_id: 订单 ID
            
        Returns:
            dict: 订单信息，如果不存在则返回 None
        """
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT id, user_id, project_id, amount, token_amount, status,
                       created_at, updated_at
                FROM subscription_orders
                WHERE id = ?
            """, [order_id]) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "project_id": row["project_id"],
                    "amount": row["amount"],
                    "token_amount": row["token_amount"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
    
    @staticmethod
    async def get_user_orders(
        user_id: str,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户的认购订单列表
        
        Args:
            user_id: 用户钱包地址（会自动转换为小写）
            project_id: 可选，筛选特定项目
            status: 可选，筛选特定状态
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            list: 订单列表（按创建时间倒序）
        """
        user_id = str(user_id).lower()
        
        query = """
            SELECT id, user_id, project_id, amount, token_amount, status,
                   created_at, updated_at
            FROM subscription_orders
            WHERE user_id = ?
        """
        params = [user_id]
        
        if project_id is not None:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "project_id": row["project_id"],
                        "amount": row["amount"],
                        "token_amount": row["token_amount"],
                        "status": row["status"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    }
                    for row in rows
                ]
    
    @staticmethod
    async def get_project_orders(
        project_id: int,
        status: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取项目的所有认购订单列表
        
        Args:
            project_id: 项目 ID
            status: 可选，筛选特定状态
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            list: 订单列表（按创建时间倒序）
        """
        query = """
            SELECT id, user_id, project_id, amount, token_amount, status,
                   created_at, updated_at
            FROM subscription_orders
            WHERE project_id = ?
        """
        params = [project_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "id": row["id"],
                        "user_id": row["user_id"],
                        "project_id": row["project_id"],
                        "amount": row["amount"],
                        "token_amount": row["token_amount"],
                        "status": row["status"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    }
                    for row in rows
                ]
    
    @staticmethod
    async def get_user_total_investment(user_id: str, project_id: int) -> Decimal:
        """
        获取用户在某个项目中的累计认购金额
        
        Args:
            user_id: 用户钱包地址（会自动转换为小写）
            project_id: 项目 ID
            
        Returns:
            Decimal: 累计认购金额（仅统计 Success 状态的订单）
        """
        user_id = str(user_id).lower()
        
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                SELECT COALESCE(SUM(CAST(amount AS REAL)), 0) as total
                FROM subscription_orders
                WHERE user_id = ? AND project_id = ? AND status = 'Success'
            """, [user_id, project_id]) as cursor:
                row = await cursor.fetchone()
                total_str = str(row[0]) if row and row[0] else "0"
                return SubscriptionModel._str_to_decimal(total_str)
    
    @staticmethod
    async def update_order_status(
        order_id: int,
        status: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        更新订单状态
        
        Args:
            order_id: 订单 ID
            status: 新状态（"Success", "Pending", "Refunded"）
            **kwargs: 其他要更新的字段
        
        Returns:
            dict: 更新后的订单信息
        """
        updates = {"status": status, **kwargs}
        
        # 转换金额字段（如果有）
        for key in ["amount", "token_amount"]:
            if key in updates:
                updates[key] = SubscriptionModel._decimal_to_str(updates[key])
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ["status", "amount", "token_amount"]:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return await SubscriptionModel.get_order(order_id)
        
        set_clauses.append("updated_at = strftime('%s', 'now')")
        params.append(order_id)
        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f"""
                UPDATE subscription_orders
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """, params)
            await db.commit()
            
            return await SubscriptionModel.get_order(order_id)
