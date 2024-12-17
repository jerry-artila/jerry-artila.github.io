# i.MX 使用 HABv4 的安全和加密啟動

## 1. 簡介
i.MX 系列處理器在片上 ROM 中提供高保證啟動 (HAB High Assurance Boot) 功能。ROM 負責從啟動媒體 (boot media) 載入初始程式映像(U-Boot),而 HAB 使 ROM 能夠通過使用密碼學操作來驗證和/或解密程式映像。

此功能支援 i.MX 50、i.MX 53、i.MX 6、i.MX 7 系列和 i.MX 8M 系列(i.MX 8M、i.MX 8MM、i.MX 8MN、i.MX 8MP 設備)。

在 doc/imx/habv4/guides/ 目錄下提供了逐步指南,熟悉 HAB 和 CST PKI 樹生成的用戶應參考這些文檔。

## 1.1 HABv4 安全啟動架構
HABv4 安全啟動功能使用數字簽名 (digital signature) 來防止在設備啟動序列期間未經授權 (unauthorized) 的軟體執行。如果惡意軟體 (malware) 控制了啟動序列,敏感數據、服務和網絡可能會受到影響。

HAB 認證基於使用 RSA 算法的公鑰密碼學 (public key cryptography),其中映像數據使用一系列私鑰離線 (offline) 簽名。然後使用相應的公鑰在 i.MX 處理器上驗證生成的已簽名映像數據 (signed image data)。公鑰包含在 CSF (Command Sequence File) 二進制文件中,而 SRK (Super Root Key) Hash 則編程在 SoC 保險絲 (fuses) 中以建立信任根 (root of trust)。

下圖說明了安全啟動過程概述:
```
          Host PC + CST                             i.MX + HAB
          +----------+                             +----------+
     ---> |  U-Boot  |                             | Compare  |
     |    +----------+                             +----------+
     |          |                                     ^    ^
     |          v                         Reference  /      \  Generated
     |    +----------+                      Hash    /        \   Hash
     |    |   Hash   |  Private                    /          \
     |    +----------+    Key                     /            \
     |          |          |                +----------+  +----------+
     |          v          |                |  Verify  |  |   Hash   |
     |    +----------+     |                +----------+  +----------+
     |    |   Sign   |  <---      SRK            ^            ^
     |    +----------+            HASH            \          /
     |          |                  |          CSF  \        /   U-Boot
     |          v                  v                \      /
     |    +----------+        +----------+        +----------+
     |    |  U-Boot  |        |          |        |  U-Boot  |
     ---> |     +    | -----> |   i.MX   | -----> |     +    |
          |    CSF   |        |          |        |    CSF   |
          +----------+        +----------+        +----------+

```

要編程到啟動媒體中的 U-Boot 映像需要正確構建,即它必須包含適當的命令序列文件 (CSF Command Sequence File)。

CSF 是由 HAB 解釋的二進制數據結構,用於指導認證過程,這是由代碼簽名工具 (CST Code Signing Tool)生成的。CSF 結構包含命令、SRK 表、簽名和證書。

關於安全啟動和代碼簽名工具 (CST) 的詳細信息可以在應用說明 AN4581 和安全啟動指南中找到。CSF 的語法和詳細信息可以在 CST 用戶指南中找到,該指南與 CST 工具一起打包並位於 doc 目錄中。

## 1.2 HABv4 加密啟動架構
在支援 CAAM 的設備中,HAB 加密啟動功能為啟動加載序列添加了額外的安全操作。它使用密碼學技術(AES-CCM)來混淆 U-Boot 數據,使未經授權的用戶無法查看或使用。此機制保護了存儲在閃存或外部記憶體中的 U-Boot 代碼,並確保最終映像對每個設備都是唯一的。

該過程可以分為兩種保護機制。第一種機制是引導加載程序代碼加密,提供數據機密性;第二種機制是數字簽名,用於驗證加密映像。

請記住,無論順序如何(先簽名後加密,或先加密後簽名),加密啟動都會使用這兩種機制,這兩種操作可以應用於同一區域,但 U-Boot 頭部(IVT、啟動數據和 DCD)除外,它只能簽名而不能加密。

下圖說明了加密啟動過程概述:

```
     Host PC + CST                                      i.MX + HAB
     +------------+                                  +--------------+
     |   U-Boot   |                                  |    U-Boot    |
     +------------+                                  +--------------+
            |                                                ^
            |                                                |
            v         DEK                            +--------------+
     +------------+    |                       ----> |    Decrypt   |
     |   Encrypt  | <---                       |     +--------------+
     +------------+                        DEK |             ^
            |                                  |             |
            |       Private                    |             |
            v         Key                  +------+   +--------------+
     +------------+    |                   | CAAM |   | Authenticate |
     |    Sign    | <---                   +------+   +--------------+
     +------------+            DEK             ^             ^
            |                + OTPMK       DEK  \           /  U-Boot
            |                   |          Blob  \         /   + CSF
            v                   v                 \       /
     +------------+       +----------+          +------------+
     | Enc U-Boot |       |          |          | Enc U-Boot |
     |   + CSF    | ----> |   i.MX   | -------> |   + CSF    |
     | + DEK Blob |       |          |          | + DEK Blob |
     +------------+       +----------+          +------------+
            ^                   |
            |                   |
            ---------------------
                   DEK Blob
                    (CAAM)
```

當加密映像時,代碼簽名工具會自動生成一個隨機的 AES 數據加密密鑰(DEK)。此密鑰用於加密和解密操作,並應以 CAAM blob 封裝的形式存在於最終映像結構中。

OTP 主密鑰(OTPMK)用於加密並將 DEK 包裝在 blob 結構中。OTPMK 對每個設備都是唯一的,只能由 CAAM 訪問。為了進一步增加 DEK 的安全性,blob 在只能由 CAAM 訪問的安全記憶體分區內解封裝和解密。

在使用 DEK blob 設計加密啟動時,有必要禁止對 DEK blob 的任何修改或用假冒的 blob 替換,以防止執行惡意代碼。CAAM 中的 PRIBLOB 設置允許安全啟動軟體擁有自己的私有 blob,這些 blob 不能被任何其他用戶代碼解封裝或封裝,包括在受信任模式下運行的任何軟體。

關於 DEK Blob 生成和 PRIBLOB 設置的詳細信息可以在加密啟動指南和應用說明 AN12056[3]中找到。

## 2. 生成 PKI 樹
第一步是生成私鑰和公鑰證書。HAB 架構基於公鑰基礎設施(PKI)樹。

代碼簽名工具包在 keys/ 目錄下包含一個基於 OpenSSL 的密鑰生成腳本。hab4_pki_tree.sh 腳本能夠生成包含多達 4 個超級根密鑰(SRK)及其從屬 IMG 和 CSF 密鑰的 PKI 樹。

可以按照以下示例生成新的 PKI 樹:
在 CST 上生成 2048 位 PKI 樹(從 v3.1.0 開始):

```
$ ./hab4_pki_tree.sh
  ...
  Do you want to use an existing CA key (y/n)?: n
  Do you want to use Elliptic Curve Cryptography (y/n)?: n
  Enter key length in bits for PKI tree: 2048
  Enter PKI tree duration (years): 5
  How many Super Root Keys should be generated? 4
  Do you want the SRK certificates to have the CA flag set? (y/n)?: y
```
下圖說明了 PKI 樹:

```
                                +---------+
                                |   CA    |
                                +---------+
                                     |
                                     |
            ---------------------------------------------------
            |               |                 |               |
            |               |                 |               |
            v               v                 v               v
       +--------+       +--------+       +--------+       +--------+
       |  SRK1  |       |  SRK2  |       |  SRK3  |       |  SRK4  |
       +--------+       +--------+       +--------+       +--------+
         /    \           /    \           /    \           /    \
        v      v         v      v         v      v         v      v
     +----+  +----+   +----+  +----+   +----+  +----+   +----+  +----+
     |CSF1|  |IMG1|   |CSF2|  |IMG2|   |CSF3|  |IMG3|   |CSF4|  |IMG4|
     +----+  +----+   +----+  +----+   +----+  +----+   +----+  +----+

```

運行腳本後,用戶可以檢查 keys/ 目錄下的私鑰及其在 crts/ 目錄下相應的 X.509v3 公鑰證書。這些文件將在簽名和認證過程中使用。

## 2.1 生成快速認證 PKI 樹
從 HAB v4.1.2 開始,用戶可以使用單個 SRK 密鑰來認證 CSF 和 IMG 內容。這減少了在 ROM/HAB 啟動階段必須進行的密鑰對認證數量,從而提供更快的啟動過程。

hab4_pki_tree.sh 腳本也能夠生成只包含 SRK 密鑰的公鑰基礎設施(PKI)樹,生成 SRK 證書時用戶不應設置 CA 標誌。

在 CST 上生成 2048 位快速認證 PKI 樹(從 v3.1.0 開始):
```
$ ./hab4_pki_tree.sh
  ...
  Do you want to use an existing CA key (y/n)?: n
  Do you want to use Elliptic Curve Cryptography (y/n)?: n
  Enter key length in bits for PKI tree: 2048
  Enter PKI tree duration (years): 5
  How many Super Root Keys should be generated? 1
  Do you want the SRK certificates to have the CA flag set? (y/n)?: n
```
下圖說明了 PKI 樹:

```
                             +---------+
                             |   CA    |
                             +---------+
                                  |
                                  |
         ---------------------------------------------------
         |               |                 |               |
         |               |                 |               |
         v               v                 v               v
    +--------+       +--------+       +--------+       +--------+
    |  SRK1  |       |  SRK2  |       |  SRK3  |       |  SRK4  |
    +--------+       +--------+       +--------+       +--------+

```


## 2.2 生成 SRK 表和 SRK 雜湊
下一步是從上述步驟中創建的 SRK 公鑰證書生成 SRK 表及其相應的 SRK 表雜湊。
在 HAB 架構中,SRK 表包含在 CSF 二進制文件中,而 SRK 雜湊則編程在 SoC SRK_HASH[255:0] 保險絲中。

在目標設備上,在認證過程中 HAB 代碼將 SRK 表與 SoC SRK_HASH 保險絲進行驗證,如果驗證成功,則建立信任根,HAB 代碼可以繼續進行映像認證。

srktool 可用於生成 SRK 表及其相應的 SRK 表雜湊。

在 Linux 64 位機器上生成 SRK 表和 SRK 雜湊:
```
$ ../linux64/bin/srktool -h 4 -t SRK_1_2_3_4_table.bin -e \
	SRK_1_2_3_4_fuse.bin -d sha256 -c \
	SRK1_sha256_2048_65537_v3_ca_crt.pem,\
	SRK2_sha256_2048_65537_v3_ca_crt.pem,\
	SRK3_sha256_2048_65537_v3_ca_crt.pem,\
	SRK4_sha256_2048_65537_v3_ca_crt.pem
```

SRK_1_2_3_4_table.bin 和 SRK_1_2_3_4_fuse.bin 文件可以在後續步驟中使用,如 doc/imx/habv4/guides/ 目錄下的 HAB 指南所述。

參考文獻:
1. CST: i.MX 高保證啟動參考代碼簽名工具
2. AN4581: "i.MX HABv4 支援設備上的安全啟動"
3. AN12056: "HABv4 和 CAAM 啟用設備上的加密啟動"
