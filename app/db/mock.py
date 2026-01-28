"""
Mock 数据库模块
用于在测试网环境下模拟用户资产数据
支持 JSON 文件持久化存储，确保数据在服务器重启后不丢失
"""
import json
import os
from pathlib import Path
from typing import Optional

# 安全导入 requests 库（防御性增强）
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

# ========== JSON 持久化配置 ==========
# 数据文件存储路径（相对于项目根目录）
DATA_DIR = Path(__file__).parent.parent.parent / "data"
ASSETS_FILE = DATA_DIR / "mock_assets.json"
ORDERS_FILE = DATA_DIR / "mock_orders.json"
POSITIONS_FILE = DATA_DIR / "mock_positions.json"
PRICES_FILE = DATA_DIR / "mock_prices.json"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)


def _load_json_file(file_path: Path, default_value):
    """
    从 JSON 文件加载数据
    
    Args:
        file_path: JSON 文件路径
        default_value: 如果文件不存在或读取失败，返回的默认值
        
    Returns:
        加载的数据（字典或列表）
    """
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[OK] 从 {file_path.name} 加载数据成功")
                return data
        else:
            print(f"[INFO] {file_path.name} 不存在，使用默认值")
            return default_value
    except Exception as e:
        print(f"[WARN] 加载 {file_path.name} 失败: {str(e)}，使用默认值")
        return default_value


def _save_json_file(file_path: Path, data):
    """
    保存数据到 JSON 文件
    
    Args:
        file_path: JSON 文件路径
        data: 要保存的数据（字典或列表）
    """
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件（使用临时文件确保原子性）
        temp_file = file_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # 原子性替换
        temp_file.replace(file_path)
        print(f"[SAVE] 保存 {file_path.name} 成功")
    except Exception as e:
        print(f"[ERROR] 保存 {file_path.name} 失败: {str(e)}")


# ========== 用户资产数据（全局唯一事实来源） ==========
# 默认资产配置（测试账号初始资金）
_DEFAULT_ASSETS = {
    # 注意：Key 必须是小写，确保地址匹配时忽略大小写
    "0xf9afea4377012b7a874c899e6462b5c66d784508": {
        # 可用余额
        "USDT": 1000000.0,  # 给足资金用于测试买入
        "BTC": 0.5,
        "ETH": 10.0,
        "BNB": 50.0,
        "SOL": 100.0,
        "DOGE": 50000.0,
        "TRX": 10000.0,
        "BEAT": 1000.0,
        "AIC": 2000.0,
        # 冻结资产（用于限价挂单）
        "USDT_frozen": 0.0,
        "BTC_frozen": 0.0,
        "ETH_frozen": 0.0,
        "BNB_frozen": 0.0,
        "SOL_frozen": 0.0,
        "DOGE_frozen": 0.0,
        "TRX_frozen": 0.0,
        "BEAT_frozen": 0.0,
        "AIC_frozen": 0.0
    },
}

def _load_assets():
    """
    从 JSON 文件加载资产数据（如果存在），否则使用默认值
    
    Returns:
        dict: 资产字典，Key 为小写地址，Value 为资产余额字典
        
    Note:
        确保所有地址键（Key）统一转换为小写，防止因大小写不匹配找不到数据
    """
    loaded_data = _load_json_file(ASSETS_FILE, _DEFAULT_ASSETS.copy())
    
    # 确保所有地址键都是小写（防止大小写不匹配）
    normalized_data = {}
    for address, assets in loaded_data.items():
        normalized_address = address.lower()
        normalized_data[normalized_address] = assets
    
    return normalized_data

def save_assets():
    """
    保存当前资产数据到 JSON 文件
    供外部调用，用于持久化资产变更
    
    Note:
        确保保存时所有地址键都是小写
    """
    # 确保所有地址键都是小写（双重保险）
    normalized_data = {}
    for address, assets in MOCK_USER_ASSETS.items():
        normalized_address = address.lower()
        normalized_data[normalized_address] = assets
    
    _save_json_file(ASSETS_FILE, normalized_data)

# 初始化资产数据（全局唯一事实来源）
# 必须在函数定义之后初始化，因为 _load_assets() 需要调用 _load_json_file() 和 ASSETS_FILE
MOCK_USER_ASSETS = _load_assets()

# Mock 订单存储
# 使用列表存储所有订单对象
# 每个订单对象包含完整的订单信息
MOCK_ORDERS = []

# Mock 持仓存储（合约交易）
# 存储用户当前的开仓信息
MOCK_POSITIONS = []

# ========== 市场价格数据（全局唯一事实来源） ==========
# 默认价格配置
_DEFAULT_PRICES = {
    "BTC/USDT": 92255.0,
    "ETH/USDT": 3100.0,
    "BNB/USDT": 590.0,
    "SOL/USDT": 145.0,
    "DOGE/USDT": 0.12,
    "TRX/USDT": 0.15,
    "BEAT/USDT": 1.2,
    "AIC/USDT": 2.0
}

def _load_prices():
    """
    从 JSON 文件加载价格数据（如果存在），否则使用默认值
    
    Returns:
        dict: 价格字典
    """
    return _load_json_file(PRICES_FILE, _DEFAULT_PRICES.copy())

# 初始化价格数据（全局唯一事实来源）
# 必须在函数定义之前初始化，因为 save_prices() 和 get_market_price() 会引用它
MOCK_MARKET_PRICES = _load_prices()

def save_prices():
    """
    保存当前价格数据到 JSON 文件
    供外部调用，用于持久化价格变更
    """
    _save_json_file(PRICES_FILE, MOCK_MARKET_PRICES)

# 全局标志：是否已打印过 requests 缺失警告（避免刷屏）
_REQUESTS_WARNING_PRINTED = False

def _get_real_time_price_from_binance(symbol: str) -> Optional[float]:
    """
    从 Binance API 获取实时价格（优先级2：实时行情）
    
    Args:
        symbol: 交易对，例如 "BTC/USDT"
        
    Returns:
        Optional[float]: 实时价格，如果获取失败则返回 None
        
    Note:
        此函数用于获取真实的市场价格，当 MOCK_MARKET_PRICES 中没有手动设置的价格时使用
        如果 requests 库不可用，将直接返回 None
    """
    # 防御性检查：如果没有 requests 库，直接返回 None
    if not HAS_REQUESTS:
        return None
    
    try:
        # 将交易对格式转换为 Binance 格式（例如 "BTC/USDT" -> "BTCUSDT"）
        binance_symbol = symbol.upper().replace('/', '')
        
        # Binance 24hr ticker price API
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}"
        
        # 发送请求（设置超时时间，避免阻塞）
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            price = float(data.get('price', 0))
            if price > 0:
                return price
    except Exception as e:
        # 静默失败，不打印错误日志（避免日志过多）
        # 如果 Binance API 不可用，返回 None，使用默认值
        pass
    
    return None


def get_market_price(symbol: str) -> float:
    """
    获取交易对的当前市场价格（带优先级判断）
    
    优先级 1 (手动覆盖)：首先检查 MOCK_MARKET_PRICES 字典中是否有该币种的值。
                         如果该值大于 0，则强制返回这个值。
    
    优先级 2 (实时行情)：如果字典里没有或者值为 0，再从 Binance API 获取真实价格。
    
    优先级 3 (默认保底)：如果都失败，返回 _DEFAULT_PRICES 中的默认值。
    
    Args:
        symbol: 交易对，例如 "BTC/USDT"
        
    Returns:
        float: 当前市场价格，如果都不存在则返回默认值或 0.0
        
    Example:
        # 如果 MOCK_MARKET_PRICES["BTC/USDT"] = 95000.0
        # 即使 Binance 实时价格是 91401，也会返回 95000（手动覆盖）
        
        # 如果 MOCK_MARKET_PRICES["BTC/USDT"] = 0 或不存在
        # 则从 Binance API 获取实时价格（例如 91401）
        
        # 如果 Binance API 也失败，返回 _DEFAULT_PRICES 中的默认值（例如 92255.0）
    """
    global _REQUESTS_WARNING_PRINTED
    
    symbol_upper = symbol.upper()
    
    # 优先级 1：检查 MOCK_MARKET_PRICES 中是否有手动设置的价格（且大于0）
    manual_price = MOCK_MARKET_PRICES.get(symbol_upper, 0.0)
    if manual_price and manual_price > 0:
        return float(manual_price)
    
    # 优先级 2：从 Binance API 获取实时价格（防御性检查）
    if HAS_REQUESTS:
        real_time_price = _get_real_time_price_from_binance(symbol_upper)
        if real_time_price is not None and real_time_price > 0:
            return real_time_price
    else:
        # 如果没有 requests 库，打印友好的警告（仅一次，避免刷屏）
        if not _REQUESTS_WARNING_PRINTED:
            print("[WARN] requests 库未安装，无法获取外部实时行情。将使用 MOCK_MARKET_PRICES 中的价格或默认值。")
            print("[WARN] 建议安装 requests: pip install requests")
            _REQUESTS_WARNING_PRINTED = True
    
    # 优先级 3：默认保底值（从 _DEFAULT_PRICES 获取）
    default_price = _DEFAULT_PRICES.get(symbol_upper, 0.0)
    if default_price > 0:
        return float(default_price)
    
    # 如果都获取不到，返回 0.0
    return 0.0


def _init_data_from_files():
    """
    初始化：从 JSON 文件加载数据（如果存在）
    在模块导入时自动执行
    
    Note:
        资产数据和价格数据已在模块顶层初始化，这里只需要加载订单和持仓数据
    """
    global MOCK_ORDERS, MOCK_POSITIONS
    
    # 注意：资产数据已在模块顶层通过 MOCK_USER_ASSETS = _load_assets() 初始化
    # 价格数据已在模块顶层通过 MOCK_MARKET_PRICES = _load_prices() 初始化
    # 这里不需要重新加载，因为它们已经会从文件读取数据
    
    # 加载订单
    loaded_orders = _load_json_file(ORDERS_FILE, MOCK_ORDERS)
    if isinstance(loaded_orders, list):
        MOCK_ORDERS = loaded_orders
    
    # 加载持仓
    loaded_positions = _load_json_file(POSITIONS_FILE, MOCK_POSITIONS)
    if isinstance(loaded_positions, list):
        MOCK_POSITIONS = loaded_positions
    
    print(f"[INIT] 数据初始化完成: 资产用户数={len(MOCK_USER_ASSETS)}, 订单数={len(MOCK_ORDERS)}, 持仓数={len(MOCK_POSITIONS)}, 价格对={len(MOCK_MARKET_PRICES)}")


# 模块加载时自动初始化
_init_data_from_files()


def get_user_assets(address: str) -> dict:
    """
    获取用户的资产余额（包含可用和冻结）
    
    Args:
        address: 钱包地址
        
    Returns:
        dict: 资产余额字典，如果用户不存在则创建默认值并保存
        
    Note:
        如果用户不存在，会自动创建默认资产结构并保存到文件，防止前端显示 0
    """
    # 将地址转换为小写（以太坊地址不区分大小写）
    address_lower = address.lower()
    
    # 增加日志打印，确认地址是否正确
    print(f"正在查询资产，当前地址: {address_lower}")
    
    # 调试日志：打印当前 MOCK_USER_ASSETS 的状态
    print(f"[DEBUG] [get_user_assets] 查询地址: {address_lower}")
    print(f"[DEBUG] [get_user_assets] 当前 MOCK_USER_ASSETS 中的地址数量: {len(MOCK_USER_ASSETS)}")
    if MOCK_USER_ASSETS:
        print(f"[DEBUG] [get_user_assets] 所有地址: {list(MOCK_USER_ASSETS.keys())[:3]}...")  # 只打印前3个
    
    # 如果用户存在，返回其资产
    if address_lower in MOCK_USER_ASSETS:
        assets = MOCK_USER_ASSETS[address_lower].copy()
        print(f"[OK] [get_user_assets] 找到用户资产: USDT={assets.get('USDT', 0)}, BTC={assets.get('BTC', 0)}")
        return assets
    
    # 如果用户不存在，创建默认资产结构并保存（防止前端显示 0）
    print(f"[WARN] [get_user_assets] 用户不存在，创建默认资产结构并保存")
    default_assets = {
        "USDT": 0.0,
        "BTC": 0.0,
        "ETH": 0.0,
        "BNB": 0.0,
        "SOL": 0.0,
        "DOGE": 0.0,
        "TRX": 0.0,
        "BEAT": 0.0,
        "AIC": 0.0,
        "USDT_frozen": 0.0,
        "BTC_frozen": 0.0,
        "ETH_frozen": 0.0,
        "BNB_frozen": 0.0,
        "SOL_frozen": 0.0,
        "DOGE_frozen": 0.0,
        "TRX_frozen": 0.0,
        "BEAT_frozen": 0.0,
        "AIC_frozen": 0.0
    }
    
    # 将默认资产结构添加到 MOCK_USER_ASSETS 并保存
    MOCK_USER_ASSETS[address_lower] = default_assets.copy()
    save_assets()
    
    print(f"[OK] [get_user_assets] 已创建并保存默认资产结构")
    return default_assets


def update_user_assets(address: str, assets: dict) -> dict:
    """
    更新用户的资产余额（自动保存到 JSON 文件）
    
    Args:
        address: 钱包地址（会自动转换为小写）
        assets: 新的资产余额字典
        
    Returns:
        dict: 更新后的资产余额
        
    Note:
        确保地址键统一转换为小写，防止因大小写不匹配找不到数据
    """
    # 确保地址键统一转换为小写
    address_lower = address.lower()
    
    # 如果用户不存在，先创建默认资产结构
    if address_lower not in MOCK_USER_ASSETS:
        MOCK_USER_ASSETS[address_lower] = {
            "USDT": 0.0,
            "BTC": 0.0,
            "ETH": 0.0,
            "BNB": 0.0,
            "SOL": 0.0,
            "DOGE": 0.0,
            "TRX": 0.0,
            "BEAT": 0.0,
            "AIC": 0.0,
            "USDT_frozen": 0.0,
            "BTC_frozen": 0.0,
            "ETH_frozen": 0.0,
            "BNB_frozen": 0.0,
            "SOL_frozen": 0.0,
            "DOGE_frozen": 0.0,
            "TRX_frozen": 0.0,
            "BEAT_frozen": 0.0,
            "AIC_frozen": 0.0
        }
    
    # 更新资产（使用小写地址作为键）
    MOCK_USER_ASSETS[address_lower].update(assets)
    
    # 立即调用 save_assets() 持久化到 JSON 文件
    save_assets()
    
    return MOCK_USER_ASSETS[address_lower].copy()


def freeze_assets(address: str, currency: str, amount: float) -> dict:
    """
    冻结用户资产（用于限价挂单）
    
    Args:
        address: 钱包地址
        currency: 币种（例如 "USDT", "BTC"）
        amount: 冻结数量
        
    Returns:
        dict: 更新后的资产余额
        
    Raises:
        ValueError: 如果可用余额不足
    """
    address_lower = address.lower()
    current_assets = get_user_assets(address_lower)
    
    # 检查可用余额是否充足
    available = current_assets.get(currency, 0.0)
    if available < amount:
        raise ValueError(f"可用余额不足。需要冻结 {amount} {currency}，当前可用: {available} {currency}")
    
    # 冻结资产：从可用余额转移到冻结余额
    current_assets[currency] = available - amount
    frozen_key = f"{currency}_frozen"
    current_assets[frozen_key] = current_assets.get(frozen_key, 0.0) + amount
    
    return update_user_assets(address_lower, current_assets)


def unfreeze_assets(address: str, currency: str, amount: float) -> dict:
    """
    解冻用户资产（订单成交或取消时）
    
    Args:
        address: 钱包地址
        currency: 币种（例如 "USDT", "BTC"）
        amount: 解冻数量
        
    Returns:
        dict: 更新后的资产余额
        
    Raises:
        ValueError: 如果冻结余额不足
    """
    address_lower = address.lower()
    current_assets = get_user_assets(address_lower)
    
    # 检查冻结余额是否充足
    frozen_key = f"{currency}_frozen"
    frozen = current_assets.get(frozen_key, 0.0)
    if frozen < amount:
        raise ValueError(f"冻结余额不足。需要解冻 {amount} {currency}，当前冻结: {frozen} {currency}")
    
    # 解冻资产：从冻结余额转移到可用余额
    current_assets[frozen_key] = frozen - amount
    current_assets[currency] = current_assets.get(currency, 0.0) + amount
    
    return update_user_assets(address_lower, current_assets)


def create_order(order_data: dict) -> dict:
    """
    创建订单记录（自动保存到 JSON 文件）
    
    Args:
        order_data: 订单信息字典，必须包含 order_id
        
    Returns:
        dict: 创建的订单信息（深拷贝）
        
    Raises:
        ValueError: 如果 order_id 为空
    """
    order_id = order_data.get("order_id")
    if not order_id:
        raise ValueError("订单ID不能为空")
    
    # 检查订单是否已存在
    for existing_order in MOCK_ORDERS:
        if existing_order.get("order_id") == order_id:
            raise ValueError(f"订单已存在: {order_id}")
    
    # 创建订单副本并添加到列表
    new_order = order_data.copy()
    MOCK_ORDERS.append(new_order)
    
    # 自动保存到 JSON 文件
    _save_json_file(ORDERS_FILE, MOCK_ORDERS)
    
    return new_order.copy()


def get_order(order_id: str) -> dict:
    """
    获取订单信息
    
    Args:
        order_id: 订单ID
        
    Returns:
        dict: 订单信息，如果不存在则返回 None
    """
    for order in MOCK_ORDERS:
        if order.get("order_id") == order_id:
            return order.copy()
    return None


def update_order_status(order_id: str, status: str, **kwargs) -> dict:
    """
    更新订单状态（自动保存到 JSON 文件）
    
    Args:
        order_id: 订单ID
        status: 新状态（例如 "FILLED", "CANCELLED"）
        **kwargs: 其他要更新的字段
        
    Returns:
        dict: 更新后的订单信息（深拷贝）
        
    Raises:
        ValueError: 如果订单不存在
    """
    # 查找订单
    order_found = None
    for order in MOCK_ORDERS:
        if order.get("order_id") == order_id:
            order_found = order
            break
    
    if order_found is None:
        raise ValueError(f"订单不存在: {order_id}")
    
    # 更新订单状态和其他字段
    order_found["status"] = status
    order_found.update(kwargs)
    
    # 自动保存到 JSON 文件
    _save_json_file(ORDERS_FILE, MOCK_ORDERS)
    
    return order_found.copy()


def get_user_available_assets(address: str) -> dict:
    """
    获取用户的可用资产余额（不包含冻结）
    
    Args:
        address: 钱包地址
        
    Returns:
        dict: 可用资产余额字典，例如 {"USDT": 50000.0, "BTC": 0.0, "BEAT": 0.0}
    """
    all_assets = get_user_assets(address)
    available = {}
    
    # 提取可用余额（排除 _frozen 字段）
    for key, value in all_assets.items():
        if not key.endswith("_frozen"):
            available[key] = value
    
    return available


def get_user_frozen_assets(address: str) -> dict:
    """
    获取用户的冻结资产余额
    
    Args:
        address: 钱包地址
        
    Returns:
        dict: 冻结资产余额字典，例如 {"USDT": 1000.0, "BTC": 0.0, "BEAT": 0.0}
    """
    all_assets = get_user_assets(address)
    frozen = {}
    
    # 提取冻结余额（只包含 _frozen 字段，并去掉 _frozen 后缀）
    for key, value in all_assets.items():
        if key.endswith("_frozen"):
            currency = key.replace("_frozen", "")
            frozen[currency] = value
    
    return frozen


def get_user_orders(address: str, status: str = None) -> list:
    """
    获取用户的订单列表
    
    Args:
        address: 钱包地址
        status: 可选，筛选特定状态的订单
        
    Returns:
        list: 订单列表（按创建时间倒序排列）
    """
    address_lower = address.lower()
    orders = []
    
    # 遍历所有订单，筛选属于该用户的订单
    for order in MOCK_ORDERS:
        # 兼容 user_id 和 address 字段
        order_user_id = order.get("user_id", "").lower()
        order_address = order.get("address", "").lower()
        
        # 如果订单属于该用户
        if order_user_id == address_lower or order_address == address_lower:
            # 如果指定了状态筛选，则只返回匹配状态的订单
            if status is None or order.get("status") == status:
                orders.append(order.copy())
    
    # 按创建时间倒序排列（最新的在前）
    # 兼容 timestamp 和 create_time 字段
    orders.sort(
        key=lambda x: x.get("timestamp") or x.get("create_time", 0),
        reverse=True
    )
    
    return orders


# ========== 合约交易相关函数 (优化版) ==========

def get_user_positions(address: str, symbol: str = None) -> list:
    """
    获取用户的持仓列表
    """
    address_lower = address.lower()
    positions = []
    
    for pos in MOCK_POSITIONS:
        # 兼容 user_id 和 address 字段
        if pos.get("user_id") == address_lower or pos.get("address") == address_lower:
            if symbol is None or pos.get("symbol") == symbol:
                # 提示：可以在 API 层调用此函数后，根据最新市价动态计算 unrealized_pnl
                positions.append(pos.copy())
                
    return positions


def update_position(address: str, symbol: str, position_data: dict) -> dict:
    """
    更新或创建持仓 (包含加仓逻辑和强平价计算)
    
    Args:
        address: 钱包地址
        symbol: 交易对
        position_data: 包含 size, entry_price, leverage, side 等最新状态的字典
    """
    address_lower = address.lower()
    
    # 1. 查找现有持仓
    found_idx = -1
    for i, pos in enumerate(MOCK_POSITIONS):
        if (pos.get("user_id") == address_lower or pos.get("address") == address_lower) and pos.get("symbol") == symbol:
            found_idx = i
            break
            
    # 2. 获取新数据的关键字段
    new_size = float(position_data.get("size", 0))
    
    # 3. 平仓/删除逻辑
    if new_size <= 0:
        if found_idx != -1:
            print(f"🔥 持仓移除: {symbol}")
            MOCK_POSITIONS.pop(found_idx)
            # 自动保存到 JSON 文件
            _save_json_file(POSITIONS_FILE, MOCK_POSITIONS)
        return None
        
    # 4. 更新或创建逻辑
    if found_idx != -1:
        # --- 现有持仓更新 ---
        # 假设 position_data 已经由 API 层处理好了均价逻辑，这里直接更新
        MOCK_POSITIONS[found_idx].update(position_data)
        
        # 自动重新计算强平价格
        current_pos = MOCK_POSITIONS[found_idx]
        lev = float(current_pos.get("leverage", 10))
        entry = float(current_pos.get("entry_price", 0))
        side = current_pos.get("side", "LONG").upper()
        
        # 强平价粗略估算公式：
        # 多单：开仓价 * (1 - 1/杠杆 + 维持保证金率0.005)
        # 空单：开仓价 * (1 + 1/杠杆 - 维持保证金率0.005)
        if side == "LONG":
            liq_price = entry * (1 - 1/lev + 0.005)
        else:
            liq_price = entry * (1 + 1/lev - 0.005)
            
        current_pos["liquidation_price"] = round(liq_price, 2)
        
        # 自动保存到 JSON 文件
        _save_json_file(POSITIONS_FILE, MOCK_POSITIONS)
        
        return current_pos.copy()
        
    else:
        # --- 创建新持仓 ---
        new_pos = position_data.copy()
        new_pos["user_id"] = address_lower
        new_pos["address"] = address_lower
        new_pos["symbol"] = symbol
        
        # 初始化强平价格
        lev = float(new_pos.get("leverage", 10))
        entry = float(new_pos.get("entry_price", 0))
        side = new_pos.get("side", "LONG").upper()
        
        if side == "LONG":
            new_pos["liquidation_price"] = round(entry * (1 - 1/lev + 0.005), 2)
        else:
            new_pos["liquidation_price"] = round(entry * (1 + 1/lev - 0.005), 2)

        MOCK_POSITIONS.append(new_pos)
        
        # 自动保存到 JSON 文件
        _save_json_file(POSITIONS_FILE, MOCK_POSITIONS)
        
        return new_pos.copy()
