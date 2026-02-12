<template>
  <div class="page-shell">
    <div class="page-title"><h2>商城+库存</h2><div class="desc">商品、库存、订单、余额联动</div></div>
    <el-tabs v-model="tab">
      <el-tab-pane label="商品/SPU-SKU" name="product">
        <el-space wrap>
          <el-input v-model="keyword" placeholder="搜索商品" style="width:220px" clearable @input="loadSku" />
          <el-autocomplete v-model="skuSuggest" :fetch-suggestions="querySku" placeholder="自动联想SKU" style="width:220px" />
          <el-button @click="loadSku">刷新</el-button>
        </el-space>
        <el-table :data="skuRows" border style="margin-top:8px">
          <el-table-column prop="category_name" label="分类" />
          <el-table-column prop="spu_name" label="SPU" />
          <el-table-column prop="sku_name_zh" label="SKU名称" />
          <el-table-column prop="available_stock" label="可用库存" width="100" />
          <el-table-column prop="warning_stock" label="预警库存" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="库存台账" name="inventory">
        <el-space>
          <el-select v-model="stockForm.sku_id" placeholder="选择SKU" style="width:220px">
            <el-option v-for="s in skuRows" :key="s.id" :label="s.sku_name_zh" :value="s.id" />
          </el-select>
          <el-input-number v-model="stockForm.quantity" :min="1" />
          <el-button type="primary" @click="stockIn">入库</el-button>
          <el-button type="warning" @click="stockOut">出库</el-button>
          <el-button @click="loadLedger">刷新台账</el-button>
        </el-space>
        <el-table :data="ledgerRows" border style="margin-top:8px">
          <el-table-column prop="sku_name" label="SKU" />
          <el-table-column prop="change_type" label="类型" width="100" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="before_stock" label="变更前" width="90" />
          <el-table-column prop="after_stock" label="变更后" width="90" />
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="订单与余额" name="order">
        <el-space>
          <el-input v-model="orderKeyword" placeholder="搜索订单/长者名" style="width:220px" clearable @input="loadOrders" />
          <el-button @click="loadOrders">刷新</el-button>
        </el-space>
        <el-table :data="orderRows" border style="margin-top:8px">
          <el-table-column prop="id" label="订单ID" min-width="180" />
          <el-table-column prop="elder_name" label="长者姓名" width="120" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="total_amount" label="总额" width="100" />
          <el-table-column label="操作" width="280">
            <template #default="scope">
              <el-space>
                <el-button size="small" @click="pay(scope.row.id)">支付</el-button>
                <el-button size="small" @click="cancel(scope.row.id)">取消</el-button>
                <el-button size="small" @click="refund(scope.row.id)">退款</el-button>
                <el-button size="small" @click="complete(scope.row.id)">完成</el-button>
              </el-space>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const tab = ref('product')
const keyword = ref('')
const skuSuggest = ref('')
const orderKeyword = ref('')
const skuRows = ref<any[]>([])
const ledgerRows = ref<any[]>([])
const orderRows = ref<any[]>([])
const stockForm = reactive({ sku_id: '', quantity: 1 })

const loadSku = async () => {
  const resp = await http.get('/shop/sku', { params: { page: 1, page_size: 10, keyword: keyword.value } })
  skuRows.value = resp.data.data.items || []
}
const loadLedger = async () => {
  const resp = await http.get('/shop/inventory/ledger', { params: { page: 1, page_size: 10 } })
  ledgerRows.value = resp.data.data.items || []
}
const loadOrders = async () => {
  const resp = await http.get('/shop/orders', { params: { page: 1, page_size: 10, keyword: orderKeyword.value } })
  orderRows.value = resp.data.data.items || []
}
const querySku = async (q: string, cb: any) => {
  const resp = await http.get('/shop/sku/suggest', { params: { keyword: q } })
  cb((resp.data.data || []).map((x: any) => ({ value: `${x.name}(${x.available_stock})` })))
}

const stockIn = async () => {
  await http.post('/shop/inventory/in', { ...stockForm, remark: '前端入库' })
  ElMessage.success('入库成功')
  loadSku(); loadLedger()
}
const stockOut = async () => {
  await http.post('/shop/inventory/out', { ...stockForm, remark: '前端出库' })
  ElMessage.success('出库成功')
  loadSku(); loadLedger()
}
const pay = async (id: string) => { await http.post(`/shop/orders/${id}/pay`); loadOrders() }
const cancel = async (id: string) => { await http.post(`/shop/orders/${id}/cancel`, { reason: '手工取消' }); loadOrders() }
const refund = async (id: string) => { await http.post(`/shop/orders/${id}/refund`, { reason: '手工退款' }); loadOrders() }
const complete = async (id: string) => { await http.post(`/shop/orders/${id}/complete`); loadOrders() }

onMounted(async () => { await loadSku(); await loadLedger(); await loadOrders() })
</script>
