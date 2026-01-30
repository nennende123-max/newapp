package ws

import (
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

type KlineData struct {
	Symbol    string  `json:"symbol"`
	Interval  string  `json:"interval"`
	Timestamp int64   `json:"timestamp"`
	Open      float64 `json:"open"`
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Close     float64 `json:"close"`
	Volume    float64 `json:"volume"`
	IsClosed  bool    `json:"is_closed"`
}

type KlineMessage struct {
	Type string    `json:"type"`
	Data KlineData `json:"data"`
}

type Hub struct {
	mu      sync.RWMutex
	clients map[*Client]struct{}
}

type Client struct {
	conn *websocket.Conn
	send chan []byte
}

func NewHub() *Hub {
	return &Hub{
		clients: make(map[*Client]struct{}),
	}
}

func (h *Hub) add(client *Client) {
	h.mu.Lock()
	h.clients[client] = struct{}{}
	h.mu.Unlock()
}

func (h *Hub) remove(client *Client) {
	h.mu.Lock()
	delete(h.clients, client)
	h.mu.Unlock()
}

func (h *Hub) broadcast(payload []byte) {
	h.mu.RLock()
	for client := range h.clients {
		select {
		case client.send <- payload:
		default:
			close(client.send)
			h.mu.RUnlock()
			h.remove(client)
			h.mu.RLock()
		}
	}
	h.mu.RUnlock()
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func HandleKlineWS(hub *Hub) gin.HandlerFunc {
	return func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			return
		}

		client := &Client{
			conn: conn,
			send: make(chan []byte, 32),
		}
		hub.add(client)

		connectedMsg, _ := json.Marshal(map[string]string{
			"type":    "connected",
			"message": "K 线实时推送已连接",
		})
		client.send <- connectedMsg

		go client.writePump(hub)
		client.readPump(hub)
	}
}

func (c *Client) readPump(hub *Hub) {
	defer func() {
		hub.remove(c)
		_ = c.conn.Close()
	}()

	c.conn.SetReadLimit(1024)
	_ = c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	c.conn.SetPongHandler(func(string) error {
		return c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
	})

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			break
		}
		var payload map[string]interface{}
		if err := json.Unmarshal(message, &payload); err != nil {
			continue
		}
		if msgType, ok := payload["type"].(string); ok && msgType == "ping" {
			pong, _ := json.Marshal(map[string]string{"type": "pong"})
			select {
			case c.send <- pong:
			default:
			}
		}
	}
}

func (c *Client) writePump(hub *Hub) {
	ticker := time.NewTicker(30 * time.Second)
	defer func() {
		ticker.Stop()
		hub.remove(c)
		_ = c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			_ = c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if !ok {
				_ = c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}
			if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
				return
			}
		case <-ticker.C:
			_ = c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

func StartKlineGenerator(hub *Hub) {
	symbols := []string{"BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "DOGE/USDT"}
	prices := map[string]float64{
		"BTC/USDT": 90000,
		"ETH/USDT": 3000,
		"BNB/USDT": 600,
		"SOL/USDT": 150,
		"DOGE/USDT": 0.08,
	}

	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	rng := rand.New(rand.NewSource(time.Now().UnixNano()))

	for range ticker.C {
		for _, symbol := range symbols {
			base := prices[symbol]
			change := base * (rng.Float64()*0.001 - 0.0005)
			closePrice := base + change
			high := closePrice + (rng.Float64() * base * 0.0003)
			low := closePrice - (rng.Float64() * base * 0.0003)
			open := base
			volume := rng.Float64()*100 + 10
			prices[symbol] = closePrice

			kline := KlineMessage{
				Type: "kline",
				Data: KlineData{
					Symbol:    symbol,
					Interval:  "1m",
					Timestamp: time.Now().UnixMilli(),
					Open:      open,
					High:      high,
					Low:       low,
					Close:     closePrice,
					Volume:    volume,
					IsClosed:  false,
				},
			}

			payload, err := json.Marshal(kline)
			if err != nil {
				log.Printf("kline marshal failed: %v", err)
				continue
			}
			hub.broadcast(payload)
		}
	}
}
