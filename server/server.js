const express = require('express');
const cors = require('cors');
const mysql = require('mysql2');

const app = express();
const PORT = 3000;

// 1. 开启跨域允许前端访问
app.use(cors());
app.use(express.json());

// 2. 连接数据库 (注意这里用你的 root1 / 123456)
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root1',         // 你的用户名
  password: '123456',    // 你的密码
  database: 'crypto_exchange',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// 3. 核心逻辑：自动初始化数据库表和数据
const initDB = () => {
    // A. 创建矿机表 (miners)
    const createTableSQL = `
        CREATE TABLE IF NOT EXISTS miners (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            period_days INT,
            price DECIMAL(10,2),
            daily_output DECIMAL(10,6),
            roi_min DECIMAL(5,2),
            roi_max DECIMAL(5,2),
            status INT DEFAULT 1
        )
    `;
    
    pool.query(createTableSQL, (err) => {
        if (err) {
            console.error('❌ 创建表失败:', err);
            return;
        }
        console.log('✅ 矿机数据表 (miners) 检查完毕');

        // B. 检查表里有没有数据，如果没有，就插入初始数据
        pool.query('SELECT COUNT(*) AS count FROM miners', (err, results) => {
            if (results[0].count == 0) {
                console.log('📦 表是空的，正在写入初始矿机数据...');
                const insertSQL = `
                    INSERT INTO miners (name, period_days, price, daily_output, roi_min, roi_max) VALUES 
                    ('BTC Experience Miner', 2, 200.00, 0.000800, 2.00, 5.00),
                    ('Advanced BTC Miner', 5, 1200.00, 0.001000, 2.00, 8.00),
                    ('Pro ASIC Miner', 12, 2500.00, 0.001160, 6.00, 20.00)
                `;
                pool.query(insertSQL, (err) => {
                    if (err) console.error('写入数据失败:', err);
                    else console.log('🎉 初始矿机数据写入成功！');
                });
            }
        });
    });
};

// 启动时初始化
initDB();

// 4. 写接口：前端获取矿机列表的 API
app.get('/api/miners', (req, res) => {
    pool.query('SELECT * FROM miners', (err, results) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({ 
            code: 200, 
            message: 'success', 
            data: results 
        });
    });
});

app.listen(PORT, () => {
    console.log(`🚀 服务端已启动: http://localhost:${PORT}`);
});