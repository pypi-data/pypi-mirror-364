- ✅ MultiModelAutoCRUD才是主要使用的class，需要被改名成AutoCRUD，原本的AutoCRUD改成其他名字
- ✅ MultiModelAutoCRUD的storage為什麼只有一個? storage應該跟resource深度綁定
- ✅ create_routes應該可以直接吐一個fastapi router出來，不需要吃app進去
- ✅ 我們應該要讓user自己建立type的id、created_time、created_by、updated_time、updated_by，再用調用的方式去access object，而不是自動地在type上面硬寫id field，不然user create出來的type無法在project內部復用 (缺id等等attribute)。i.e., user需要創建最完整的schema，包含id, created_time, ...。我們必須根據這個schema自動推倒出
    1.create的body需要長甚麼樣(e.g., 不需要有id, times，不需要udated_by，created_by可選是從function取得或是必須在body中(function取得可能是透過request cookie)
    2. update的body (前面敘述過)，也不需要有id、created_time、created_by、updated_time、updated_by，但是一樣update_by要讓user可選是從哪來。
- ✅ get應該回傳list of resource，而不是dict
- ✅ 新增created_time、created_by、updated_time、updated_by，這些項目是optional，可以選擇是否開啟，以及開啟之後的attribute name是甚麼
- ✅ key name可選，預設用id沒問題，但可以讓user選擇其他名稱，例如pk、_id等等
- ✅ update使用特殊的updater，對每個attribute做細部adjust，而不是每次都要傳完整的body
    - ✅ undefined: 不改變
    - ✅ 有值: 改成該值
    - ✅ list attribute: 提供"改整個list"，"新增items by list[value]"，"刪除items by list[value]"
    - ✅ dict attribute: 提供"改整個dict"，"新增items by dict[key, value]"，"刪除items by list[key]"
- ✅ 我應該能夠直接使用AutoCRUD (和MultiModelAutoCRUD)新增route
- ✅ 每個route應該都要可選，而不是一股腦全部給出去
- 列出所有資源應該要能吃params來support
  1. pagination
  2. filter by created_by/updated_by (list)
  3. filter by created_time/updated_time (range)
  4. sort by created_time/updated_time (incr/decr)
- ✅ typing，希望可以可以使用typing方法，例如AutoCRUD[XXX]來指定這個crud的resource type
