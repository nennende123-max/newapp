package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

func main() {
	router := gin.Default()
	router.GET("/ws", handleWS)

	if err := router.Run(":8080"); err != nil {
		log.Fatalf("server start failed: %v", err)
	}
}

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

type KlinePayload struct {
	Time   int64   `json:"time"`
	Open   float64 `json:"open"`
	High   float64 `json:"high"`
	Low    float64 `json:"low"`
	Close  float64 `json:"close"`
	Volume float64 `json:"volume"`
}

type binanceKlineMessage struct {
	K binanceKline `json:"k"`
}

type binanceKline struct {
	T int64  `json:"t"`
	O string `json:"o"`
	H string `json:"h"`
	L string `json:"l"`
	C string `json:"c"`
	V string `json:"v"`
}

func handleWS(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		return
	}
	defer conn.Close()

	done := make(chan struct{})
	go func() {
		defer close(done)
		forwardBinanceKlines(conn)
	}()

	for {
		if _, _, err := conn.ReadMessage(); err != nil {
			return
		}
	}
}

func forwardBinanceKlines(clientConn *websocket.Conn) {
	const wsURL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
	retryDelay := 2 * time.Second

	for {
		binanceConn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
		if err != nil {
			log.Printf("binance dial failed: %v", err)
			time.Sleep(retryDelay)
			continue
		}

		for {
			_, message, err := binanceConn.ReadMessage()
			if err != nil {
				_ = binanceConn.Close()
				log.Printf("binance read failed: %v", err)
				break
			}

			var payload binanceKlineMessage
			if err := json.Unmarshal(message, &payload); err != nil {
				continue
			}

			open, err := strconv.ParseFloat(payload.K.O, 64)
			if err != nil {
				continue
			}
			high, err := strconv.ParseFloat(payload.K.H, 64)
			if err != nil {
				continue
			}
			low, err := strconv.ParseFloat(payload.K.L, 64)
			if err != nil {
				continue
			}
			closePrice, err := strconv.ParseFloat(payload.K.C, 64)
			if err != nil {
				continue
			}
			volume, err := strconv.ParseFloat(payload.K.V, 64)
			if err != nil {
				continue
			}

			clean := KlinePayload{
				Time:   payload.K.T,
				Open:   open,
				High:   high,
				Low:    low,
				Close:  closePrice,
				Volume: volume,
			}

			data, err := json.Marshal(clean)
			if err != nil {
				continue
			}
			if err := clientConn.WriteMessage(websocket.TextMessage, data); err != nil {
				_ = binanceConn.Close()
				log.Printf("client write failed: %v", err)
				return
			}
		}

		time.Sleep(retryDelay)
	}
}
