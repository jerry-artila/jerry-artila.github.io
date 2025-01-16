# Modbus PDU

## 1. 定義

Modbus PDU 是 Modbus 協議核心的數據包

## 2. 結構

Modbus PDU 由兩個部分組成：

1. 功能碼 (Function Code)
   - 1 byte
   - 定義要執行的操作類型
   - 範圍: 1-127 (0x01-0x7F)
   - 錯誤回應時最高位元設為 1 (0x80-0xFF)

2. 數據區 (Data)
   - 長度可變
   - 包含請求的參數或回應的數據
   - 最大長度取決於通訊協定
   - 請求和回應的格式依功能碼而定

## 3. 例子

### 例子 1: 讀取保持寄存器 (Read Holding Registers)

請求 PDU:
- 功能碼: 0x03 (讀取保持寄存器)
- 數據區:
  - 起始地址: 0x006B (2 bytes)
  - 寄存器數量: 0x0003 (2 bytes)

回應 PDU:
- 功能碼: 0x03
- 數據區:
  - 字節數: 0x06 (1 byte)
  - 寄存器值: 0x022B, 0x0000, 0x0064 (6 bytes)

### 例子 2: 寫入單一線圈 (Write Single Coil)

請求 PDU:
- 功能碼: 0x05 (寫入單一線圈)
- 數據區:
  - 線圈地址: 0x00AC (2 bytes)
  - 線圈值: 0xFF00 (ON) 或 0x0000 (OFF) (2 bytes)

回應 PDU:
- 功能碼: 0x05
- 數據區:
  - 線圈地址: 0x00AC (2 bytes)
  - 線圈值: 0xFF00 (ON) 或 0x0000 (OFF) (2 bytes)

# Modbus ADU (Application Data Unit)

ADU 是完整的 Modbus 通訊數據包，包含了 PDU 和額外的通訊相關資訊。ADU 的結構依通訊協定而異：

### Modbus RTU ADU 結構

1. 從站地址 (Slave Address)
   - 1 byte
   - 範圍: 1-247
   - 0 為廣播地址
   
2. PDU
   - 功能碼 (1 byte)
   - 數據區 (N bytes)

3. CRC校驗 (CRC-16)
   - 2 bytes
   - 用於錯誤檢測

### Modbus TCP ADU 結構

1. MBAP 標頭 (Modbus Application Protocol Header)
   - 事務處理識別碼 (2 bytes): 用於配對請求和回應，由客戶端生成的唯一識別碼。當服務器回應時會返回相同的識別碼，使客戶端能夠將回應與對應的請求匹配起來。這在處理多個並發請求時特別重要。
   - 協定識別碼 (2 bytes): 固定為 0x0000
   - 長度 (2 bytes): 後續資料的長度
   - 單元識別碼 (1 byte): 相當於從站地址

2. PDU
   - 功能碼 (1 byte)
   - 數據區 (N bytes)

### 比較

- RTU ADU 較簡單，適合串列通訊
- TCP ADU 增加了網路通訊所需的資訊
- PDU 在兩種格式中保持不變，確保協議的一致性

### ADU 範例

1. RTU ADU 範例 (寫入單一線圈)
   - 從站地址: 0x11 (17)
   - PDU:
     - 功能碼: 0x05
     - 線圈地址: 0x00AC
     - 線圈值: 0xFF00 (ON)
   - CRC: 0x4E8F
   
   完整數據包: 11 05 00 AC FF 00 4E 8F

2. TCP ADU 範例 (寫入單一線圈)
   - MBAP 標頭:
     - 事務處理識別碼: 0x0001
     - 協定識別碼: 0x0000  
     - 長度: 0x0006 (6 bytes，包含單元識別碼1byte + 功能碼1byte + 數據區4bytes)
     - 單元識別碼: 0x11 (17) - 用於識別特定的從站設備。在網關或橋接設備中特別有用，可以用來路由訊息到其他網路中的設備。在直接的TCP/IP連接中通常設為0xFF。
   - PDU:
     - 功能碼: 0x05
     - 線圈地址: 0x00AC
     - 線圈值: 0xFF00 (ON)
   
   完整數據包: 00 01 00 00 00 06 11 05 00 AC FF 00



